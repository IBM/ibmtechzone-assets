from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import ibm_db_dbi
import pandas as pd
from typing import List, Optional

app = FastAPI()

class Ticket(BaseModel):
    VIN_CODE: str
    DATE: str

@app.get("/query_db", response_model=List[Ticket])
def query_db(
    dsn_database: str = Query(..., description="Database name"),
    dsn_hostname: str = Query(..., description="Hostname"),
    dsn_port: int = Query(..., description="Port"),
    dsn_uid: str = Query(..., description="User ID"),
    dsn_pwd: str = Query(..., description="Password"),
    sql_query: Optional[str] = Query("SELECT VIN_CODE, DATE FROM KLK42673.TICKET;", description="SQL query to execute")
):
    # Create the connection string
    dsn = (
        f"DATABASE={dsn_database};"
        f"HOSTNAME={dsn_hostname};"
        f"PORT={dsn_port};"
        f"PROTOCOL=TCPIP;"
        f"UID={dsn_uid};"
        f"PWD={dsn_pwd};"
        f"SECURITY=SSL;"
    )

    # Establish the connection
    try:
        print("Before connection call")
        conn = ibm_db_dbi.connect(dsn, "", "")
        cursor = conn.cursor()
        print("Connected to the database")
    except Exception as e:
        print("Unable to connect to the database")
        raise HTTPException(status_code=500, detail=f"Unable to connect to the database: {str(e)}")
    
    try:
        cursor.execute(sql_query)
        df = pd.read_sql_query(sql_query, conn)
        print("Data extracted from TICKET table successfully!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to execute query: {str(e)}")
    finally:
        # Close the connection
        if conn:
            conn.close()
            print("Connection closed")

    return df.to_dict(orient='records')
