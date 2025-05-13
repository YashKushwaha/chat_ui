## WIP

import sqlite3
import pandas as pd

# Feeding tables into the database
# Example if stored in a pandas DataFrame:
# df_meta = pd.read_excel("column_metadata.xlsx")

column_descriptions = {}
for _, row in df_meta.iterrows():
    table = row['table_name']
    col = row['column_name']
    desc = row['description']
    column_descriptions.setdefault(table, {})[col] = desc



# Connect to DB
conn = sqlite3.connect("patients.db")
cursor = conn.cursor()

# List tables
def list_tables():
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [row[0] for row in cursor.fetchall()]

tables = list_tables()
print("Tables:", tables)

# Get Column Metadata for Each Table
def describe_table(table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    # columns: [cid, name, type, notnull, dflt_value, pk]
    return pd.DataFrame(columns, columns=["cid", "name", "type", "notnull", "default", "pk"])

# Example: describe first table
describe_table(tables[0])


# View sample data
def sample_rows(table_name, limit=5):
    return pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT {limit};", conn)

# Example
sample_rows(tables[0])


# Combine into LLM prompt 
def generate_schema_summary():
    summary = ""
    for table in tables:
        summary += f"\nTable: {table}\n"
        df_meta = describe_table(table)
        summary += "Columns:\n"
        for _, row in df_meta.iterrows():
            summary += f"  - {row['name']} ({row['type']})\n"
        df_sample = sample_rows(table)
        summary += "Sample rows:\n"
        summary += df_sample.to_string(index=False)
        summary += "\n" + "-"*40 + "\n"
    return summary

schema_summary = generate_schema_summary()
print(schema_summary)

# Creating prompt for LLM
prompt = f"""
You are a SQL expert with access to the following database schema:

{schema_summary}

The user wants to know: "Do patients with low physical activity have higher BMI?"

Generate a valid SQL query that can be run on this data.
"""