if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
from script.get_offer_status import get_offer_status
from script.update_status_of_offers_table_by_offer_id import update_status_of_offers_table_by_offer_id


def update_status_of_offers_table_of_all_offers(db_path: str):

    # Connect to the SQLite database (it will create the database file if it doesn't exist)
    conn = sqlite3.connect(db_path)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # SQL query to retrieve all offer_ids with status not equal to 'Deleted'
    query = "SELECT offer_id FROM offers WHERE status != 'Deleted'"
    
    # Execute the query
    cursor.execute(query)
    
    # Fetch all results in a list
    offer_ids = [row[0] for row in cursor.fetchall()]

    for offer_id in offer_ids:
        
        update_status_of_offers_table_by_offer_id(cursor, offer_id)

    conn.commit()
    conn.close()



if __name__ == '__main__':

    db_path = "D:\DeFi\YAM_indexing\YAM.db"
    
    update_status_of_offers_table_of_all_offers(db_path)