import prestodb
from minio import Minio
import pandas as pd
from io import BytesIO
from datetime import datetime
import numpy as np
import requests

usa_states = {'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR', 'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE', 
              'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID', 'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS', 'kentucky': 'KY', 
              'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD', 'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS', 'missouri': 'MO', 
              'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV', 'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY', 'north carolina':'NC',
              'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK', 'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC', 
              'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT', 'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV', 
              'wisconsin': 'WI', 'wyoming': 'WY'}

def create_address_input(row):
    """
    Create a formatted address string from the street address, street address2, and country columns of a DataFrame row.

    Args:
        row (Series): A row of the DataFrame containing street address, street address2, and country columns.

    Returns:
        str: The formatted address string.
    """
    if row['street_address'] != row['street_address2']:
        address = row['street_address'] + row['street_address2']
    else:
        address= row['street_address']    
    address = address +', ' + str(row['country'])
    return address


def parse_mailing_address(address):
    """
    Parse the mailing address using Google Maps Geocoding API.

    Args:
        address (str): The address to parse.

    Returns:
        dict: A dictionary containing parsed address components including city, state, postal code, latitude, and longitude.
    """
    params = {
        'key': "GOOGLE_GEOCODING_API_KEY",
        'address': address
        }

    base_url = "https://maps.googleapis.com/maps/api/geocode/json?"
    data = requests.get(base_url, params= params).json()
    if data['results']:
            result = data['results'][0]
            components = result['address_components']
            city = next((comp['long_name'] for comp in components if 'locality' in comp['types']), None)
            state = next((comp['long_name'] for comp in components if 'state' in comp['types']), None)
            postal_code = next((comp['long_name'] for comp in components if 'postal_code' in comp['types']), None)
            location = result['geometry']['location']
            latitude = location['lat']
            longitude = location['lng']
            resultDict= {
                 'city': city,
                 'state': state,
                 'postal_code': postal_code,
                 'latitude': latitude,
                 'longitude': longitude
                 }
    else:
        resultDict= {
                 'city': '',
                 'state': '',
                 'postal_code': '',
                 'latitude': '',
                 'longitude': ''
                 }

    return resultDict

def validate_address(df):
    """
    Validate addresses in a DataFrame and update city, postal code, state/province, latitude, and longitude if available.

    Args:
        df (DataFrame): The DataFrame containing addresses to be validated.

    Returns:
        DataFrame: The DataFrame with validated address details.
    """
    counter = 0
    for index, row in df.iterrows():
        if row['street_address']:
            counter += 1
            address = create_address_input(row)
            correct_address = parse_mailing_address(address)
            if correct_address['city']:
                df.loc[index, 'city'] = str(correct_address['city'])
            if correct_address['postal_code']:
                df.loc[index, 'city'] = str(correct_address['city'])
            if correct_address['state']:
                df.loc[index, 'state_province'] = str(correct_address['state'])
            if correct_address['latitude']:
                df.loc[index, 'latitude'] = str(correct_address['latitude'])
            if correct_address['state']:
                df.loc[index, 'longitude'] = str(correct_address['longitude'])

        if counter == 10:
            break
    return df


def state_correction(text):
    """
    Correct the input text to match the standardized format for state names.

    Args:
        text (str): The input text representing a state name.

    Returns:
        str: The corrected state name if found in the dictionary of USA states, otherwise returns the original input text.
    """
    lower_text = text.lower().strip()  # Convert text to lowercase and remove leading/trailing spaces
    if lower_text in list(usa_states.keys()):  # Check if the lowercase text matches a state abbreviation
        return usa_states[lower_text]  # Return the standardized state name
    return text  # Return the original input text if no match is found


def convert_ownership(val):
    """
    Convert ownership status from full text to abbreviation.

    Args:
        val (str): The ownership status.

    Returns:
        str: The abbreviated ownership status ('O' for Owned, 'L' for Leased) if the input matches, otherwise returns the original input.
    """
    if val.lower() == 'owned':  # Check if the input value is 'owned' in lowercase
        return 'O'  # Return 'O' for Owned
    elif val.lower() == 'leased':  # Check if the input value is 'leased' in lowercase
        return 'L'  # Return 'L' for Leased
    else:
        return val  # Return the original input if it does not match 'owned' or 'leased'


def floor_correction(text):
    """
    Correct floor names to a standard format.

    Args:
        text (str): The floor name.

    Returns:
        str: The corrected floor name if it matches the mapping, otherwise returns the original input.
    """
    floor_mapping = {
        '1st': '1st Floor', 'first': '1st Floor', 'first flr': '1st Floor',
        '2nd': '2nd Floor', 'second': '2nd Floor', 'second flr': '2nd Floor',
        '3rd': '3rd Floor', 'third': '3rd Floor', 'third flr': '3rd Floor',
        '4th': '4th Floor', 'fourth': '4th Floor', 'fourth flr': '4th Floor',
        '5th': '5th Floor', 'fifth': '5th Floor', 'fifth flr': '5th Floor',
        '6th': '6th Floor', 'sixth': '6th Floor', 'sixth flr': '6th Floor',
        '7th': '7th Floor', 'seventh': '7th Floor', 'seventh flr': '7th Floor',
        '8th': '8th Floor', 'eighth': '8th Floor', 'eighth flr': '8th Floor',
        '9th': '9th Floor', 'ninth': '9th Floor', 'ninth flr': '9th Floor',
        '10th': '10th Floor', 'tenth': '10th Floor', 'tenth flr': '10th Floor'
    }
    lower_text = text.lower().strip()
    if lower_text in floor_mapping:
        return floor_mapping[lower_text]
    return text


def connect_PrestoDB(dbHost='na4.services.cloud.techzone.ibm.com',
                     dbPort=48931,
                     dbUser='ibmlhadmin',
                     dbCatalog='tpch',
                     dbSchema='tiny',
                     dbHttp_scheme='https',
                     dbCert = 'lh-ssl-ts-2.crt'):
     """
    Establish a connection to PrestoDB and return a cursor object for executing queries.

    Parameters:
    - dbHost (str): The hostname or IP address of the PrestoDB server. Default is 'na4.services.cloud.techzone.ibm.com'.
    - dbPort (int): The port number of the PrestoDB server. Default is 48931.
    - dbUser (str): The username for authentication. Default is 'ibmlhadmin'.
    - dbCatalog (str): The catalog to use. Default is 'tpch'.
    - dbSchema (str): The schema to use. Default is 'tiny'.
    - dbHttp_scheme (str): The HTTP scheme to use ('http' or 'https'). Default is 'https'.
    - dbCert (str): The path to the SSL certificate file for verifying the server's SSL certificate.
                    Default is 'lh-ssl-ts-2.crt'.

    Returns:
    - Cursor: A cursor object for executing queries on the PrestoDB connection.

    Notes:
    - This function establishes a connection to PrestoDB using the provided parameters and returns a cursor object.
    - The default values are provided for typical usage, but they can be overridden as needed.
    """
     prestoconn = prestodb.dbapi.connect(
         host=dbHost,
         port=dbPort,
         user=dbUser,
         catalog=dbCatalog,
         schema=dbSchema,
         http_scheme=dbHttp_scheme,
         auth=prestodb.auth.BasicAuthentication("ibmlhadmin", "password")
         )
     prestoconn._http_session.verify = dbCert
     curr = prestoconn.cursor()
     return curr

def create_minio_client():
    """
    Create and return a MinIO client object configured with the provided credentials.

    Returns:
    - Minio: A MinIO client object configured with the provided credentials.

    Notes:
    - The MinIO client is initialized with the endpoint, access key, and secret key.
    - The `secure` parameter is set to False to allow connection without SSL/TLS encryption.
    """
    minio_client = Minio(
        endpoint='na4.services.cloud.techzone.ibm.com:24273',
        access_key='c4oA1wEGYpYdadvHZEeH',
        secret_key='9tJQCjsODdEoQ9al8DP5uxYfTJ3ekyPkxoZba3yV',
        secure=False
    )

    return minio_client

def drop_subset_keys(dictionary):
    """
    Drops keys from the input dictionary if their values are subsets of values of other keys for the same working table.

    Args:
        dictionary (dict): The input dictionary containing keys and their associated values.

    Returns:
        dict: The modified dictionary after removing keys that are subsets of values of other keys.
    """
    keys_to_remove = []  # List to store keys to be removed
    for key1 in dictionary:
        for key2 in dictionary:
            if key1 != key2:
                # Extract working table names from the keys
                working_table_name1 = list(dictionary[key1])[0]
                working_table_name2 = list(dictionary[key2])[0]
                # Check if both keys belong to the same working table
                if working_table_name1 == working_table_name2:
                    # Get column names associated with each key
                    column_key1 = list(dictionary[key1][working_table_name1].keys())
                    column_key2 = list(dictionary[key2][working_table_name2].keys())
                    # Check if the columns of key1 are a subset of columns of key2
                    if set(column_key1).issubset(set(column_key2)):
                        keys_to_remove.append(key1)  # Add key1 to keys_to_remove
                        break  # No need to check further if key1 is subset of key2
    # Remove keys that are subsets of values of other keys
    for key in keys_to_remove:
        del dictionary[key]
    return dictionary  # Return the modified dictionary


def create_working_df():
    """
    Creates two empty DataFrames representing the property and floors/rooms data.

    Returns:
        tuple: A tuple containing two pandas DataFrames:
               - The first DataFrame represents the property data.
               - The second DataFrame represents the floors/rooms data.
    """
    # Define column names for property and floors/rooms data
    property_columns = ['property_id', 'client', 'property_name', 'type', 'subtype', 'status', 'ownership', 'area_unit_of_measure', 'gross_area', 'net_area', 'country', 
                        'ignore_address_suggestions', 'street_address', 'street_address2', 'city', 'state_or_province', 'postal_code', 'latitude', 'longitude', 'client_property_id', 
                        'client_property_name', 'client_property_type', 'client_property_subtype', 'regionnumber', 'divisionnumber', 'employeenumber', 'employeenumber2',
                        'dateopened', 'groupname', 'typename', 'altkey', 'phonenumber', 'tcc_project_number', 'product_type', 'tcc_business_unit', 'owner_entity', 
                        'square_feet', 'userdef1', 'userdef2', 'employeenumber3', 'timezone', 'daylight', 'landlordvendor', 'landlordvendorsite', 'propmgmtvendor', 
                        'propmgmtvendorsite', 'leaseown', 'leaserenewal', 'leaseexpire', 'facilitytype', 'countrycode', 'filterseq', 'localeid', 'servicecenterid', 'address3', 'address4', 
                        'tech1', 'tech2', 'locationemail', 'trsautodispatch', 'busclockstart', 'busclockend', 'dateclosed', 'nteapprovalcode', 'defaultpremployee']
    floors_rooms_columns = ['property_name', 'floor_id', 'floor_description', 'floor_user_defined_1', 'floor_user_defined_2', 'room_id', 'room_name', 'reference1', 'reference2', 'reference3', 'reference4']
    
    # Create empty DataFrames with defined column names
    df1 = pd.DataFrame(columns=property_columns)
    df2 = pd.DataFrame(columns=floors_rooms_columns)
    
    return df1, df2  # Return a tuple of DataFrames


def create_sql_fetch_column_names(schema, table_name):
    """
    Create SQL query to fetch column names of a table in a specified schema.

    Args:
        schema (str): The name of the schema where the table is located.
        table_name (str): The name of the table for which to fetch column names.

    Returns:
        str: The SQL query to fetch column names.
    """
    generatedSQL = f"""SHOW COLUMNS FROM hive_data.{schema}.{table_name}"""
    
    return generatedSQL


def load_data_hive(conn, schema, table_name):
    """
    Load data from a Hive table using the provided connection object.

    Args:
        conn: The connection object for interacting with the Presto database.
        schema (str): The name of the schema where the table is located.
        table_name (str): The name of the table from which to load the data.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the loaded data, or an empty DataFrame if an error occurs during loading.
    """
    try:
        # Construct SQL query to select all data from the specified table
        sql_data = f"""SELECT * FROM hive_data.{schema}.{table_name}"""
        
        # Execute the SQL query to fetch all rows from the table
        conn.execute(sql_data)
        
        # Fetch all rows from the executed query
        rows = conn.fetchall()
        
        # Construct SQL query to fetch column names of the table
        sql_column = create_sql_fetch_column_names(schema, table_name)
        
        # Execute the SQL query to fetch column names
        conn.execute(sql_column)
        
        # Fetch column names from the executed query
        columns_name = conn.fetchall()
        
        # Create a pandas DataFrame using the fetched rows and column names
        df = pd.DataFrame(rows, columns=[col[0] for col in columns_name])
        
        return df  # Return the DataFrame containing the loaded data
    except Exception as e:
        print(f"An error occurred while loading data from Hive: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if an error occurs


def pandas_to_presto_type(pandas_type):
    """
    Converts a Pandas data type to the corresponding Presto SQL data type.

    Parameters:
    - pandas_type (type): The Pandas data type to be converted.

    Returns:
    - str: The corresponding Presto SQL data type.

    Examples:
    >>> pandas_to_presto_type(int)
    'BIGINT'
    >>> pandas_to_presto_type(float)
    'DOUBLE'
    >>> pandas_to_presto_type(bool)
    'BOOLEAN'
    >>> pandas_to_presto_type(pd.Timestamp)
    'TIMESTAMP'
    >>> pandas_to_presto_type(pd.Timedelta)
    'VARCHAR'
    """
    if issubclass(pandas_type, (np.integer, np.int64, np.int32)):
        return 'BIGINT'
    elif issubclass(pandas_type, (np.floating, np.float64, np.float32)):
        return 'DOUBLE'
    elif issubclass(pandas_type, np.bool_):
        return 'BOOLEAN'
    elif issubclass(pandas_type, (np.datetime64, pd.Timestamp)):
        return 'TIMESTAMP'
    elif issubclass(pandas_type, (np.timedelta64, pd.Timedelta)):
        return 'VARCHAR'
    else:
        return 'VARCHAR'
    

def create_sql_schema(schema, table_name):
    """
    Generate SQL query to create a Hive schema with the specified name and location.

    Args:
        schema (str): The name of the schema.
        table_name (str): The name of the table associated with the schema.

    Returns:
        str: The SQL query to create the schema.
    """
    generatedSQL = f"""create schema hive_data.{schema} with (location = 's3a://hive-bucket/{schema}')"""
    return generatedSQL


def create_sql_table(schema, table_name, column_dict):
    """
    Generate SQL query to create a Hive table with the specified schema, table name, and column definitions.

    Args:
        schema (str): The name of the schema.
        table_name (str): The name of the table.
        column_dict (dict): A dictionary where keys are column names and values are data types.

    Returns:
        str: The SQL query to create the table.
    """
    # Initialize SQL query string
    sql_query = f"CREATE TABLE hive_data.{schema}.{table_name} ("

    # Iterate over the column dictionary to construct columns and data types
    for col_name, data_type in column_dict.items():
        # Append column name and data type to SQL query
        sql_query += f"{col_name} {data_type}, "

    # Remove trailing comma and space from the last column definition
    sql_query = sql_query.rstrip(', ') + f""") WITH (format = 'CSV', external_location='s3a://hive-bucket/{schema}/{table_name}')"""

    return sql_query

def create_hive_tables(schema, table_name, presto_data_types):
    """
    Create Hive tables based on the provided schema, table name, and Presto data types.

    Args:
        schema (str): The schema name for the Hive table.
        table_name (str): The name of the Hive table.
        presto_data_types (dict): A dictionary mapping column names to their corresponding Presto data types.

    Returns:
        tuple: A tuple containing the result of executing the SQL schema creation query and the result of executing the SQL table creation query.
    """
    conn = connect_PrestoDB()  # Establish connection to PrestoDB
    SQL_schema = create_sql_schema(schema, table_name)  # Generate SQL query to create schema
    try:
        res1 = conn.execute(SQL_schema)  # Execute SQL query to create schema
    except Exception as e:
        res1 = e  # Capture exception if schema creation fails
    try:
        SQL_table = create_sql_table(schema, table_name, presto_data_types)  # Generate SQL query to create table
        res2 = conn.execute(SQL_table)  # Execute SQL query to create table
    except Exception as e:
        res2 = e  # Capture exception if table creation fails
    return res1, res2  # Return the results of schema and table creation


def create_iceberg_updated_tables(conn, schema1, schema2, table_name):
    """
    Create an updated Iceberg table in the specified schema by copying data from a Hive table in another schema.

    Args:
        conn: The connection object to interact with the database.
        schema1 (str): The name of the schema where the updated Iceberg table will be created.
        schema2 (str): The name of the schema where the source Hive table resides.
        table_name (str): The name of the table to be created and copied.

    Returns:
        str or None: Returns None if the operation is successful. Otherwise, returns the error message.
    """
    try:
        sql_query = f"""CREATE TABLE iceberg_data.{schema1}.{table_name}
                    AS SELECT * FROM hive_data.{schema2}.{table_name}"""
        conn.execute(sql_query)
    except Exception as e:
        return str(e)


def working_table_1(schema, mappings):
    """
    Generates and updates tables for a given schema based on mappings.

    Args:
        schema (str): The name of the schema where tables will be created.
        mappings (list of dict): A list of dictionaries containing mapping information.
            Each dictionary should have the following keys:
                - 'is_mapped' (bool): Indicates if the column is mapped.
                - 'file_name' (str): The name of the file containing the column.
                - 'working_table' (str): The name of the working table.
                - 'column_name' (str): The name of the column in the working table.
                - 'target_data_column_name' (str): The name of the corresponding column in the target table.

    Returns:
        None
    """
    conn = connect_PrestoDB()
    minio_client = create_minio_client()
    global_mapping = {}
    schema = schema.replace(' ', '_')
    schema = schema.replace('-', '_')
    schema = schema.lower()
    for ele in mappings:
        if ele['is_mapped']:
            table_name = ele['file_name'].split('.csv')[0]
            table_name = table_name.replace(' ', '_')
            table_name = table_name.replace('-', '_')
            table_name = table_name.replace('&', '_')
            if table_name in global_mapping.keys():
                global_mapping[table_name][ele['working_table']][ele['column_name']] = ele['target_data_column_name']
            else:
                global_mapping[table_name] = {}
                global_mapping[table_name][ele['working_table']] = {}
                global_mapping[table_name][ele['working_table']][ele['column_name']] = ele['target_data_column_name']
    schema1 = 'iceberg_'+schema
    global_mapping = drop_subset_keys(global_mapping)
    df_property, df_floors_rooms_full = create_working_df()
    property_flag = False
    floors_flag = False
    dfs_dict = {}
    for key in global_mapping.keys():
        if list(global_mapping[key].keys())[0] == 'property':
            columns_mapping = global_mapping[key]['property']
            df = load_data_hive(conn, schema, key)
            df = df[list(columns_mapping.keys())]
            df.rename(columns=columns_mapping, inplace=True)
            
            df_property = pd.concat([df_property, df], axis=0, ignore_index=True)
            property_flag = True
        else:
            columns_mapping = global_mapping[key]['floors_and_rooms']
            df = load_data_hive(conn, schema, key)
            dfs_dict[key] = [df, columns_mapping]
            floors_flag = True
    
    df1_flag = False
    df2_flag = False
    if len(dfs_dict) == 2:
        for key in dfs_dict:
            if 'room_package' in dfs_dict[key][0].columns.tolist():
                df1 = dfs_dict[key][0]
                df1_mapping = dfs_dict[key][1]
                df1_flag = True
            elif 'floor_type' in dfs_dict[key][0].columns.tolist():
                df2 = dfs_dict[key][0]
                df2_mapping = dfs_dict[key][1]
                df2_flag = True
    if df1_flag and df2_flag:
        df_floors_rooms = pd.merge(df1, df2, how='left', left_on='room_package', right_on='floor_type')
        df_floors_rooms.drop(columns=['floor_type'])
        del df2_mapping['floor_type']
        columns_drop = []
        for key, value in df2_mapping.items():
            if value in list(df1_mapping.values()):
                columns_drop.append(key)
        for key in columns_drop:
            del df2_mapping[key]
        rename_columns = {}
        for col in df_floors_rooms.columns:
            if col.endswith('_y'):
                columns_drop.append(col)
            elif col.endswith('_x'):
                rename_columns[col] = col[:-2]
        df_floors_rooms = df_floors_rooms.drop(columns=columns_drop)
        df_floors_rooms.rename(columns=rename_columns, inplace=True)
        final_mapping = dict(**df1_mapping, **df2_mapping)
        df_floors_rooms = df_floors_rooms[list(final_mapping.keys())]
        df_floors_rooms.rename(columns=final_mapping, inplace=True)
        # df_floors_rooms = df_floors_rooms[list(final_mapping.values())]
        df_floors_rooms = pd.concat([df_floors_rooms_full, df_floors_rooms], axis=0, ignore_index=True)
    else:
        df_floors_rooms = df_floors_rooms_full
        for key in dfs_dict.keys():
            df = dfs_dict[key][0]
            columns_mapping = dfs_dict[key][1]
            df = df[list(columns_mapping.keys())]
            df.rename(columns=columns_mapping, inplace=True)
            # df = df[list(columns_mapping.values())]
            df_floors_rooms = pd.concat([df_floors_rooms, df], axis=0, ignore_index=True)

    for col in df_property.columns:
        df_property[col] = df_property[col].astype(object)
    for col in df_floors_rooms.columns:
        df_floors_rooms[col] = df_floors_rooms[col].astype(object)
    df_property = df_property.where(pd.notna(df_property), None)
    df_floors_rooms = df_floors_rooms.where(pd.notna(df_floors_rooms), None)
    df_property = address_validation.validate_address(df_property)
    df_property['state_or_province'] = df_property['state_or_province'].apply(lambda x: address_validation.state_correction(x) if x else None)
    df_property['ownership'] = df_property['ownership'].apply(lambda x: address_validation.convert_ownership(x) if x else None)
    df_floors_rooms['floor_description'] = df_floors_rooms['floor_description'].apply(lambda x: address_validation.floor_correction(x) if x else None)
    sql_schema = f"""create schema iceberg_data.{schema1.lower()} WITH (location = 's3a://iceberg-bucket/{schema1.lower()}')"""
    try:
        conn.execute(sql_schema)
    except Exception as e:
        res = e
    if property_flag:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        table_name = 'property'
        new_table_name = f"{table_name}_{timestamp_str}"
        df_property.replace(np.nan, None, inplace=True)
        filepath = schema+f"/{new_table_name}/{new_table_name}.csv"
        buffer = BytesIO()
        df_property.to_csv(buffer, header=False, index=False)
        buffer.seek(0)
        result = minio_client.put_object(bucket_name='hive-bucket', object_name=filepath, data=buffer, length=buffer.getbuffer().nbytes)
        presto_data_types = {col: pandas_to_presto_type(df_property[col].dtype.type) for col in df_property.columns}
        res1, res2 = create_hive_tables(schema, new_table_name, presto_data_types)
        create_iceberg_updated_tables(conn, schema1.lower(), schema.lower(), new_table_name)
    if floors_flag:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        table_name = 'floors_and_rooms'
        new_table_name = f"{table_name}_{timestamp_str}"
        filepath = schema+f"/{new_table_name}/{new_table_name}.csv"
        buffer = BytesIO()
        df_floors_rooms.to_csv(buffer, header=False, index=False)
        buffer.seek(0)
        result = minio_client.put_object(bucket_name='hive-bucket', object_name=filepath, data=buffer, length=buffer.getbuffer().nbytes)
        presto_data_types = {col: pandas_to_presto_type(df_floors_rooms[col].dtype.type) for col in df_floors_rooms.columns}
        res1, res2 = create_hive_tables(schema, new_table_name, presto_data_types)
        create_iceberg_updated_tables(conn, schema1.lower(), schema.lower(), new_table_name)

if __name__ == '__main__':
    mappings = str(input('Enter the mappings between target and source table columns: '))
    project_name = str(input('Enter project folder name: '))
    working_table_1(project_name, mappings)
