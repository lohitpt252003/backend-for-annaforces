from services.database_service import get_db, close_db_connection

print("Attempting to connect to MongoDB...")
db = get_db()

if db is not None:
    print("Successfully received database object.")
    print(f"Database name: {db.name}")
else:
    print("Failed to get database object.")

# Close the connection
close_db_connection()
