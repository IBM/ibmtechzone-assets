import os
import pandas as pd
import numpy as np
        
def read_data(input_file):
    try:
        df = pd.read_excel(input_file)
        return df.loc[20:434, ["Field", "Value", "Current or Future Offer"]].reset_index(drop=True)
    except Exception as e:
        print(f"Error reading file {input_file}: {e}")
        return pd.DataFrame()

def transform_data(df):
    data_dict = df.to_dict()
    transformed_data = {}

    for i in range(len(data_dict["Field"])):
        field_value = data_dict["Field"][i]
        value = data_dict["Value"].get(i, None)

        if field_value not in transformed_data:
            transformed_data[field_value] = []

        transformed_data[field_value].append(value)

    max_length = max(len(lst) for lst in transformed_data.values())

    for field_value, values in transformed_data.items():
        transformed_data[field_value] += [None] * (max_length - len(values))

    return pd.DataFrame(transformed_data)

def format_dataframe(df):
    df['PartNumber'] = df['PartNumber'].apply(lambda x: str(x).split()[0] if x else x)
    required_columns = ['PartNumber', 'Qty', 'CoverageStart', 'CoverageEnd', 'BidUnitSVP', 'BidExtSVP']
    df = df[required_columns][:-1]

    df.rename(columns={
        'PartNumber': 'Part #', 
        'CoverageStart': 'Start Date',
        'CoverageEnd': 'End Date',
        'BidUnitSVP': 'Unit list',
        'BidExtSVP': 'Ext list'
    }, inplace=True)

    # Add new columns with default values
    new_cols = ['Action', 'Status', 'Long_Desc', 'Months', 'Billing_Frequency', 
                'Ext_Net_Sell_Price', 'Sell_Price', 'Adj_cost', 'ext_Adj_cost', 
                'Disc', 'GP', 'opportunity_ID', 'SAM', 'Solution_id']
    for col in new_cols:
        df[col] = ''

    # Reorder columns
    column_order = ['Part #', 'Qty', 'Action', 'Status', 'Long_Desc', 'Months', 
                    'Billing_Frequency', 'Ext_Net_Sell_Price', 'Sell_Price', 
                    'Adj_cost', 'ext_Adj_cost', 'Unit list', 'Ext list', 'Disc', 
                    'GP', 'opportunity_ID', 'SAM', 'Solution_id', 'Start Date', 'End Date']
    df = df[column_order]

    return df

# def add_random_data(df):
#     columns_with_random_int = ['ext_Adj_cost', 'Adj_cost', 'Ext_Net_Sell_Price', 'Sell_Price', 'Billing_Frequency', 'SAM', 'Months', 'Disc', 'GP']
#     for col in columns_with_random_int:
#         df[col] = np.random.randint(100, 10000, len(df))

#     df['Solution_id'] = np.random.choice(['BP', 'P'], size=len(df))
#     return df

def add_random_data(df):
    """Adds specified random data to specific columns."""
    df['ext_Adj_cost'] = np.random.randint(1000, 100000, len(df))
    df['Adj_cost'] = np.random.randint(100, 10000, len(df))
    df['Ext_Net_Sell_Price'] = np.random.randint(100, 10000, len(df))
    df['Sell_Price'] = np.random.randint(100, 10000, len(df))
    df['Billing_Frequency'] = np.random.randint(1, 15, len(df))
    df['SAM'] = np.random.randint(100, 10000, len(df))
    df['Months'] = np.random.randint(1, 7, len(df))
    df['Disc'] = np.random.randint(1, 14, len(df))
    df['GP'] = np.random.randint(1, 6, len(df))
    df['Solution_id'] = np.random.choice(['BP', 'P'], size=len(df))

    return df


def format_currency_and_percentage(df):
    currency_cols = ['ext_Adj_cost', 'Adj_cost', 'Ext_Net_Sell_Price', 'Sell_Price']
    for col in currency_cols:
        df[col] = df[col].map('${:,.2f}'.format)

    percentage_cols = ['Disc', 'GP']
    for col in percentage_cols:
        df[col] = df[col].map('{:,.2f}%'.format)

    return df


def split_and_save(df, input_file):
    # Splitting the filename from its extension
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    current_df = df.iloc[:5, :]
    future_df = df.iloc[5:, :]

    # Using the base name in the output file names
    current_df.to_csv(f'{base_name}_current.csv')
    current_df.to_excel(f'{base_name}_current.xlsx')
    future_df.to_csv(f'{base_name}_future.csv')
    future_df.to_excel(f'{base_name}_future.xlsx')

    # Save as JSON
    current_df.to_json(f'{base_name}_current.json', orient='records')
    future_df.to_json(f'{base_name}_future.json', orient='records')

# Update the main function accordingly
def main():
    input_file = '0019697613.xlsx'
    df = read_data(input_file)
    transformed_df = transform_data(df)
    formatted_df = format_dataframe(transformed_df)
    df_with_random_data = add_random_data(formatted_df)
    final_df = format_currency_and_percentage(df_with_random_data)
    split_and_save(final_df, input_file)

if __name__ == "__main__":
    main()
