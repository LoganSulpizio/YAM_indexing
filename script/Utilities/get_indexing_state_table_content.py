import sqlite3

def get_indexing_state(db_path = "YAM.db", print_output = False):
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

    if print_output:
        print(str(output_message))
    else:
        return rows

if __name__ == "__main__":
    get_indexing_state(print_output = True)