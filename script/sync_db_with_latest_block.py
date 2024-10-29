if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
from script.index_logs_manually import index_manually
from script.Utilities.contract_data import contract_data
from script.Utilities.write_logs import write_log

def sync_db_with_latest_block(db_path: str, latest_block: int, block_per_request, w3):

    write_log(f"Syncing DB to latest block {latest_block}", 'logfile/logfile_indexingYAM.txt')

    # Connect to the SQLite database (it will create the database file if it doesn't exist)
    conn = sqlite3.connect(db_path)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM indexing_state ORDER BY indexing_id DESC LIMIT 1")
    last_row = cursor.fetchone()
    last_block_in_db = last_row[2]

    if latest_block - last_block_in_db > block_per_request:
        index_manually(w3, contract_data['YAM']['address'], last_block_in_db + 1, latest_block, block_per_request, db_path)

    conn.close()

if __name__ == '__main__':
    import json
    from web3 import Web3

    db_path = 'YAM.db'
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)

    w3 = Web3(Web3.HTTPProvider(config['w3_url3']))

    latest_block = w3.eth.block_number
    
    sync_db_with_latest_block(db_path, latest_block, w3)
