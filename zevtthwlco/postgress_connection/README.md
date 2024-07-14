# POSTGRES DB CONNECTION MANAGEMENT

This Python script provides functionality to manage tables in a PostgreSQL database. It allows you to:
1. Create a table from a CSV file.
2. List all tables in the database.
3. Delete a specified table from the database.

## Prerequisites

- Python 3.x
- PostgreSQL database
- Required Python libraries: `pandas`, `psycopg2`, `sqlalchemy`, `python-dotenv`

## Setup

1. **Install necessary libraries:**

```bash
pip install pandas psycopg2 psycopg2-binary sqlalchemy python-dotenv
