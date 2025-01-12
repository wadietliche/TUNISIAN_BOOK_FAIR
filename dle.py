import sqlite3

# Connect to the SQLite database
connection = sqlite3.connect('instance\\TUNISIAN_BOOK_FAIR.db')
cursor = connection.cursor()

# Rename the new table to books
cursor.execute('''ALTER TABLE books_temp RENAME TO books;''')

# Commit the changes and close the connection
connection.commit()
connection.close()

print("Successfully updated the books table with ISBN and UNIQUE constraint.")
