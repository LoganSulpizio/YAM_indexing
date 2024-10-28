if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
from typing import List, Dict, Any
from script.get_offer_status import get_offer_status
from script.Utilities.write_logs import write_log

def add_events_to_db(db_path, from_block, to_block, decoded_logs: List[Dict], write_timestamp = False):

    # Connect to the SQLite database (it will create the database file if it doesn't exist)
    conn = sqlite3.connect(db_path)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    
    for log in decoded_logs:

        if log['topic'] == 'OfferCreated':
            
            insert_query = """
                INSERT INTO offers (offer_id, seller_address, initial_amount, price_per_unit, offer_token, buyer_token, transaction_hash, block_number, log_index
            """
            
            # Add creation_timestamp if write_timestamp is True
            if write_timestamp:
                insert_query += ", creation_timestamp"
            
            # Complete the query
            insert_query += ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?"
            
            # Add a placeholder for CURRENT_TIMESTAMP if write_timestamp is True
            if write_timestamp:
                insert_query += ", CURRENT_TIMESTAMP"
            
            # Close the VALUES part of the query
            insert_query += ")"

            try:          
                # Execute the query and insert the data
                cursor.execute(insert_query, (log['offerId'], log['seller'], str(log['amount']), str(log['price']), log['offerToken'], log['buyerToken'], log['transactionHash'], log['blockNumber'], log['logIndex']))
            
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed: offers.offer_id' in str(e):
                    pass
                else:
                    raise e # Re-raise the exception if it's not the specific UNIQUE constraint error

        elif log['topic'] == 'OfferAccepted':

            unique_id = f"{log['transactionHash']}_{log['logIndex']}"

            insert_query = """
                INSERT INTO offer_events (offer_id, event_type, buyer_address, amount_bought, transaction_hash, block_number, log_index, unique_id
            """
            
            # Add event_timestamp if write_timestamp is True
            if write_timestamp:
                insert_query += ", event_timestamp"
            
            # Complete the query
            insert_query += ") VALUES (?, ?, ?, ?, ?, ?, ?, ?"
            
            # Add a placeholder for CURRENT_TIMESTAMP if write_timestamp is True
            if write_timestamp:
                insert_query += ", CURRENT_TIMESTAMP"
            
            # Close the VALUES part of the query
            insert_query += ")"
            
            try:
                cursor.execute(insert_query, (log['offerId'], log['topic'], log['buyer'], str(log['amount']), log['transactionHash'], log['blockNumber'], log['logIndex'], unique_id))
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed: offer_events.unique_id' in str(e):
                    pass
                else:
                    raise e # Re-raise the exception if it's not the specific UNIQUE constraint error
            
            conn.commit()

            status = get_offer_status(cursor, log['offerId'])

            if status is not None and status != 'InProgress':
                # SQL query to update the related row in the offers table
                update_query = """
                    UPDATE offers
                    SET status = ?
                    WHERE offer_id = ?
                """
                
                # Execute the query to update the status in the offers table
                cursor.execute(update_query, (status, log['offerId'],))

        elif log['topic'] == 'OfferUpdated':

            unique_id = f"{log['transactionHash']}_{log['logIndex']}"

            # SQL query to insert data into the offers table
            insert_query = """
                INSERT INTO offer_events (offer_id, event_type, amount, price, transaction_hash, block_number, log_index, unique_id
            """
            
            # Add event_timestamp if write_timestamp is True
            if write_timestamp:
                insert_query += ", event_timestamp"
            
            # Complete the query
            insert_query += ") VALUES (?, ?, ?, ?, ?, ?, ?, ?"
            
            # Add a placeholder for CURRENT_TIMESTAMP if write_timestamp is True
            if write_timestamp:
                insert_query += ", CURRENT_TIMESTAMP"
            
            # Close the VALUES part of the query
            insert_query += ")"

            try:
                # Execute the query and insert the data
                cursor.execute(insert_query, (log['offerId'], log['topic'], str(log['newAmount']), str(log['newPrice']), log['transactionHash'], log['blockNumber'], log['logIndex'], unique_id))
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed: offer_events.unique_id' in str(e):
                    pass
                else:
                    raise e # Re-raise the exception if it's not the specific UNIQUE constraint error
            
            # SQL query to update the related row in the offers table (set status to 'Deleted')
            update_query = """
                UPDATE offers
                SET status = 'InProgress'
                WHERE offer_id = ?
            """
            
            # Execute the query to update the status in the offers table
            cursor.execute(update_query, (log['offerId'],))

        elif log['topic'] == 'OfferDeleted':

            unique_id = f"{log['transactionHash']}_{log['logIndex']}"

            # SQL query to insert data into the offers table
            insert_query = """
                INSERT INTO offer_events (offer_id, event_type, transaction_hash, block_number, log_index, unique_id
            """
            
            # Add event_timestamp if write_timestamp is True
            if write_timestamp:
                insert_query += ", event_timestamp"
            
            # Complete the query
            insert_query += ") VALUES (?, ?, ?, ?, ?, ?"
            
            # Add a placeholder for CURRENT_TIMESTAMP if write_timestamp is True
            if write_timestamp:
                insert_query += ", CURRENT_TIMESTAMP"
            
            # Close the VALUES part of the query
            insert_query += ")"

            try:
                # Execute the query and insert the data
                cursor.execute(insert_query, (log['offerId'], log['topic'], log['transactionHash'], log['blockNumber'], log['logIndex'], unique_id))
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed: offer_events.unique_id' in str(e):
                    pass
                else:
                    raise e # Re-raise the exception if it's not the specific UNIQUE constraint error
                
            # SQL query to update the related row in the offers table (set status to 'Deleted')
            update_query = """
                UPDATE offers
                SET status = 'Deleted'
                WHERE offer_id = ?
            """

            # Execute the query to update the status in the offers table
            cursor.execute(update_query, (log['offerId'],))


    ### indexing_state ###
    cursor.execute("SELECT * FROM indexing_state ORDER BY indexing_id DESC LIMIT 1")
    most_recent_entry = cursor.fetchone()
    
    if  most_recent_entry is not None and most_recent_entry[2] == from_block - 1:

        # SQL query to update the related row in the indexing_state table
        update_query = """
            UPDATE indexing_state
            SET to_block = ?
            WHERE indexing_id = ?
        """

        # Execute the query to update the indexing state
        cursor.execute(update_query, (to_block, most_recent_entry[0]))

    else:

        # Insert the new entry into indexing_status
        cursor.execute("""
            INSERT INTO indexing_state (from_block, to_block)
            VALUES (?, ?)
        """, (from_block, to_block))
    
    

    # Commit the transaction to save the changes
    conn.commit()
    
    # Close the connection
    conn.close()

    write_log(f"{len(decoded_logs)} event(s) written to DB", 'logfile/logfile_indexingYAM.txt')
    
if __name__ == "__main__":
    from web3 import Web3
    from pprint import pprint
    import json
    from script.get_and_decode_logs_YAM import get_log_YAM_https, decode_logs_YAM
    from script.Utilities.contract_data import contract_data
    #w3 = Web3(Web3.HTTPProvider('https://go.getblock.io/a3dacad4a2e542aca148ed133b3a76b8'))
    #w3 = Web3(Web3.HTTPProvider('https://lb.nodies.app/v1/028d151f22f34f1f8e5137a928f0ee96'))
    w3 = Web3(Web3.HTTPProvider('https://gnosis-mainnet.blastapi.io/9330add1-83d0-4f95-b445-326506a5d029'))
    #w3 = Web3(Web3.HTTPProvider('https://nd-684-905-991.p2pify.com/3aa16c5117029835a16cdd2534cfe4a9'))
    contract_address = contract_data['YAM']['address']  # Replace with your contract address
    from_block = 36000000  # You can specify the starting block number
    to_block = 36000100  # 'latest' to get up to the most recent block
    logs = get_log_YAM_https(w3, contract_address, from_block, to_block)
    logs2 = get_log_YAM_https(w3, contract_address, from_block, to_block)
    decoded_logs = decode_logs_YAM(logs+logs2)
    #pprint(decoded_logs)
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
    db_path = config['db_path']
    add_events_to_db(db_path, from_block, to_block, decoded_logs)
            
            
            