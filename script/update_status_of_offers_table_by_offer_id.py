
if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
from script.get_offer_status import get_offer_status

def update_status_of_offers_table_by_offer_id(cursor: sqlite3.Cursor, offer_id: int):
    
    status = get_offer_status(cursor, offer_id)

    if status is not None:
        
        # SQL query to update the related row in the offers table
        update_query = """
            UPDATE offers
            SET status = ?
            WHERE offer_id = ?
        """
        
        # Execute the query to update the status in the offers table
        cursor.execute(update_query, (status, offer_id))

if __name__ == "__main__":
    
    db_path = "D:\DeFi\YAM_indexing\YAM.db"
    offer_id = 60082

    # Connect to the SQLite database (it will create the database file if it doesn't exist)
    conn = sqlite3.connect(db_path)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    update_status_of_offers_table_by_offer_id(cursor, offer_id)

    conn.commit()
    conn.close()