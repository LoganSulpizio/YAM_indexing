import sqlite3

def get_indexing_state(db_path = "YAM.db"):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute the query to select all rows from the 'indexing_state' table
    cursor.execute("SELECT * FROM indexing_state")
    
    # Fetch all rows
    rows = cursor.fetchall()

    output_message = ''

    for row in rows:
        output_message += f"{row}\n"
    
    # Close the connection
    conn.close()

    print(str(output_message))

if __name__ == "__main__":
    get_indexing_state()