import sqlite3

def get_indexing_state(db_path = "YAM.db"):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute the query to select all rows from the 'indexing_state' table
    cursor.execute("SELECT * FROM indexing_state")
    
    # Fetch all rows
    rows = cursor.fetchall()

    for row in rows:
        print(row)
    
    # Close the connection
    conn.close()

if __name__ == "__main__":
    get_indexing_state()