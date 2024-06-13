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
        'key': "*******************",
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
