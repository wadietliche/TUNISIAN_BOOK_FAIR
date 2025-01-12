import sqlite3

# Connect to the SQLite database
connection = sqlite3.connect('instance\\TUNISIAN_BOOK_FAIR.db')
cursor = connection.cursor()

# Specify the attendee_id to delete
attendee_id = 1

# Execute the SQL command to delete records from the favorite_authors table where the attendee_id matches
cursor.execute("""
    DELETE FROM favorite_authors
    WHERE attendee_id = ?
""", (attendee_id,))

# Commit the changes and close the connection
connection.commit()

# Check how many rows were affected (deleted)
print(f"Deleted {cursor.rowcount} rows from the favorite_authors table.")
connection.close()
