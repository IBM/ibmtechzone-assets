# Import necessary libraries
import os
import pandas as pd
from dotenv import load_dotenv
import psycopg2
from sqlalchemy import create_engine, MetaData, Table


# Function to load environment variables
def load_env():
    load_dotenv()
    database_name = os.getenv("DATABASE_NAME")
    username = os.getenv("DATABASE_USERNAME")
    password = os.getenv("DATABASE_PASSWORD")
    hostname = os.getenv("DATABASE_HOSTNAME")
    port = os.getenv("DATABASE_PORT")
    return database_name, username, password, hostname, port


# Function to connect to the PostgreSQL database
def connect_to_db(database_name, username, password, hostname, port):
    try:
        conn = psycopg2.connect(
            dbname=database_name, user=username, password=password, host=hostname, port=port
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


# Function to create a SQLAlchemy engine
def create_sqlalchemy_engine(database_name, username, password, hostname, port):
    try:
        engine = create_engine(f'postgresql://{username}:{password}@{hostname}:{port}/{database_name}')
        return engine
    except Exception as e:
        print(f"Error creating SQLAlchemy engine: {e}")
        return None


# Function to create a table in the database from a CSV file
def create_table_in_db_from_csv_file(conn, table_name, csv_file):
    cursor = conn.cursor()

    # Generate a SQL statement to create a table based on the CSV file structure
    df = pd.read_csv(csv_file, nrows=1)
    columns = df.columns
    sql_statement = f"CREATE TABLE {table_name} ("
    for col in columns:
        sql_statement += f"{col} VARCHAR(2000),"
    sql_statement = sql_statement.rstrip(',') + ");"

    try:
        cursor.execute(sql_statement)
        with open(csv_file, 'r') as f:
            cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER", f)
        conn.commit()
        print("Table created successfully")
    except Exception as e:
        print(f"Error creating table: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


# Function to check for tables present in the database
def check_for_tables_present_db(sql_engine):
    connection = sql_engine.connect()
    # Reflect database schema
    metadata = MetaData()
    metadata.reflect(bind=sql_engine)

    # Get list of table names
    table_names = metadata.tables.keys()
    # Print table names
    print("Tables in the database:")
    for table_name in table_names:
        print(table_name)
    connection.close()
    return list(table_names)


# Function to delete a table from the database
def delete_the_table_from_database(sql_engine, table_name):
    try:
        # Reflect database schema
        metadata = MetaData()
        metadata.reflect(bind=sql_engine)
        # Get the specified table
        table = Table(table_name, metadata, autoload_with=sql_engine)
        # Drop the table if it exists
        table.drop(sql_engine)
        print(f"Table {table_name} dropped successfully.")
    except Exception as e:
        print(f"Error dropping table {table_name}: {e}")


# Main function to run the script
def main():
    database_name, username, password, hostname, port = load_env()
    conn = connect_to_db(database_name, username, password, hostname, port)
    sql_engine = create_sqlalchemy_engine(database_name, username, password, hostname, port)

    if conn and sql_engine:
        table_name = input("Enter the table name to create: ")
        csv_file = input("Enter the path to the CSV file: ")
        create_table_in_db_from_csv_file(conn, table_name, csv_file)

        # Check for tables in the database
        check_for_tables_present_db(sql_engine)

        # Optionally delete a table
        delete_table = input("Enter the table name to delete (or press Enter to skip): ")
        if delete_table:
            delete_the_table_from_database(sql_engine, delete_table)


if __name__ == "__main__":
    main()
