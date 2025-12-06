import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('chat_logs.db')
cursor = conn.cursor()

# List tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in database:", tables)

# Assuming the table is named 'logs', fetch data
# Replace 'logs' with your actual table name if different
df = pd.read_sql_query("SELECT * FROM logs", conn)

# Print the table
print(df)

try:
    from tabulate import tabulate
    print(tabulate(df, headers='keys', tablefmt='psql'))
except ImportError:
    print("Install tabulate for pretty table: pip install tabulate")

# Save to CSV
df.to_csv('chat_logs_output.csv', index=False)
print("Data saved to chat_logs_output.csv")

# Close connection
conn.close()