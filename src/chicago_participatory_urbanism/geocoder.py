import pandas as pd

# address point csv from https://hub-cookcountyil.opendata.arcgis.com/datasets/5ec856ded93e4f85b3f6e1bc027a2472_0/about
df = pd.read_csv('data//geocode/Address_Points.csv')



def get_street_address_coordinates_from_full_name(address: str):
    """
    Return the GPS coordinates of a street address in Chicago.

    Parameters:
    - address (string): A street address in Chicago matching the following format: "1763 W BELMONT AVE"

    Returns:
    - (float, float): A tuple containing the longitude and latitude.
    """
    result = df[df['CMPADDABRV'] == address.upper()]

    try:
        longitude = result["Long"].iloc[0]
        latitude = result["Lat"].iloc[0]
    except:
        (longitude, latitude) = (0,0)
    
    return (longitude, latitude)



def get_street_address_coordinates(address_number: int, direction_abbr: str, street_name: str, street_name_post_type_abbr: str, fuzziness: int = 10):
    """
    Return the GPS coordinates of a street address in Chicago.

    Parameters:
    - address_number (int): A street number in Chicago. Ex: 1736
    - direction_abbrev (str): An abbreviated cardinal direction. Ex: "W"
    - street_name (str): A street name in Chicago. Ex: "BELMONT"
    - street_name_post_type_abbr (str): An abbreviated street type. Ex: "AVE"
    - fuzziness (int): The number of addresses +/- the desired address number when searching for coordinates. The function will always return the closest address' coordinates.
        

    Returns:
    - (float, float): A tuple containing the longitude and latitude.
    """
    results = df[(address_number - fuzziness <= df['Add_Number']) &
                (df['Add_Number'] <= address_number + fuzziness) &
                (df['LSt_PreDir'] == direction_abbr.upper()) &
                (df['St_Name'] == street_name.upper()) &
                (df['LSt_Type'] == street_name_post_type_abbr.upper())]
    
    # print(results[['Add_Number', 'St_Name','Long','Lat']])

    exact_address = results[results['Add_Number'] == address_number]

    try:
        if not exact_address.empty:
            # use exact address
            longitude = exact_address["Long"].iloc[0]
            latitude = exact_address["Lat"].iloc[0]
        else:
            # find closest address
            results['difference'] = abs(results['Add_Number'] - address_number)
            closest_index = results['difference'].idxmin()
            longitude = results.loc[closest_index, "Long"]
            latitude = results.loc[closest_index, "Lat"]
    except:
        (longitude, latitude) = (0, 0)
    
    return (longitude, latitude)


def get_intersection_coordinates(street1: str, street2: str):
    """
    Return the GPS coordinates of an intersection in Chicago.

    Parameters:
    - street1 (str): A street name in Chicago matching the format "W BELMONT AVE".
    - street2 (str): A street name in Chicago matching the format "N CLARK ST".

    Returns:
    - (float, float): A tuple containing the longitude and latitude.
    """
    # TO DO

    return (0,0)