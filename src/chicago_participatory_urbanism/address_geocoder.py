from typing import Type, Any
import os
import requests
import pandas as pd
from dotenv import load_dotenv
from address_format_processing import LocationFormat, LocationStringProcessor


load_dotenv()


class StreetCenterline:
# https://data.cityofchicago.org/Transportation/Street-Center-Lines/6imu-meau
# address point csv from https://hub-cookcountyil.opendata.arcgis.com/datasets/5ec856ded93e4f85b3f6e1bc027a2472_0/about
# headers to query socrata api
# https://dev.socrata.com/foundry/data.cityofchicago.org/pr57-gg9e
    api_header = {
        'Accept': 'application/json',
        'X-App-Token': os.getenv('app_token'),
    }

    def __init__(self,
                 add_string: str = None,
                 add_processor: Any = LocationStringProcessor,
                 ) -> None:

        self.address_string = add_string
        self.processor = add_processor

        # variable to track street names and format type return by processor
        self.streets = None
        self.format = None
        # variable to keep multi_strings return by API
        self.multiStrings = set()

        if self.address_string is not None:
            self.run_processor()

    def __repr__(self) -> str:
        return repr(self.streets)

    def run_processor(self):
        'run street text processor'

        processing = (
            self.processor(location_string=self.address_string).run()
        )

        self.streets = processing['proc_string']
        self.format = processing['format']

        return processing

    def query_api(self,
                  params: dict,
                  sql_func: str = None) -> str:
        # https://data.cityofchicago.org/Transportation/Street-Center-Lines/6imu-meau
        # https://dev.socrata.com/foundry/data.cityofchicago.org/pr57-gg9e
        # dataset metadata : https://data.cityofchicago.org/dataset/transportation/pr57-gg9e
        '''
            useful query fields:
            "the_geom" --multiline geometry
            "street_nam" street name
            "street_typ" street type, (AVE/ST)
            "pre_dir" street direction value (N/S/W/E)
            "f_cross" From Cross. Contain the cross street attribution parsed by "|", which refers to the intersecting street
                     segments at the beginning and end of each street segment respe
            "t_cross" to cross
            "logiclf" left from street number
            "logiclt" to street number
        '''
        base_link = "https://data.cityofchicago.org/resource/pr57-gg9e.json?$where="
        query_params = ' AND '.join(k + ' like ' + "'"+str(v).upper() + "'"
                                for k, v in params.items())

        if sql_func is not None:
            '''
            example:
            link = ("https://data.cityofchicago.org/resource/pr57-gg9e.json?$where=street_nam='ARTESIAN' AND street_typ='AVE' " +
                    "AND f_cross like '%2568TH%25'")
            '''
            sql_func_string = 'AND ' + sql_func
            link = base_link + query_params + sql_func_string
            resp = requests.get(link, headers=self.api_header)
            return resp.json()

        link = base_link + query_params
        resp = requests.get(link, headers=self.api_header)
        return resp.json()

    def find_intersections(self,
                           ):

        return None
    
    def find_alley(self):
        
        return None
        

    def download_centerline_to_dataframe(self) -> pd.DataFrame:
        'in case we need to download the entire file into dataframe'
        download_link = 'https://data.cityofchicago.org/api/views/pr57-gg9e/rows.csv?accessType=DOWNLOAD'

        return pd.read_csv(download_link, index_col=None)


if __name__ == '__main__':
    loc_1 = 'W FULLERTON AVE &  N WESTERN AVE&N ARTESIAN AVE &  W ALTGELD ST; 2440 N WESTERN AVE'
    loc_2 ='N MILWAUKEE AVE & N WASHTENAW AVE'
    loc_3 = '5300-5330 S PRAIRIE AVE'
    loc_4 = 'ON W 70TH ST FROM S GREEN ST (830 W) TO S PEORIA ST (900 W)'
    loc_5 = '434-442 E 46TH PL'
    loc_6 = 'E MADISON PARK & S DORCHESTER AVE & S WOODLAWN AVE & E 50TH ST'
    loc_7 = 'ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)'
    loc_8 = 'N WOOD ST & W AUGUSTA BLVD & W CORTEZ ST & N HERMITAGE AVE'
    print(StreetCenterline(
            loc_7,
            ).format
    )
    print(StreetCenterline(
            add_string=loc_7
            ).streets
    )
'''
def get_street_address_coordinates_from_full_name(address: str) -> 'Point':
    """
    Return the GPS coordinates of a street address in Chicago.

    Parameters:
    - address (string): A street address in Chicago matching the following format: "1763 W BELMONT AVE"

    Returns:
    - Point: A Shapely point with the GPS coordinates of the address (longitude, latitude).
    """
    result = df[df['CMPADDABRV'] == address.upper()]

    try:
        longitude = result["Long"].iloc[0]
        latitude = result["Lat"].iloc[0]
    except:
        (longitude, latitude) = (0,0)

    return Point(longitude, latitude)


def get_street_address_coordinates(address_number: int,
                                   direction_abbr: str,
                                   street_name: str,
                                   street_type_abbr: str,
                                   fuzziness: int = 10) -> Optional['Point']:
    """
    Return the GPS coordinates of a street address in Chicago.

    Parameters:
    - address_number (int): A street number in Chicago. Ex: 1736
    - direction_abbrev (str): An abbreviated cardinal direction. Ex: "W"
    - street_name (str): A street name in Chicago. Ex: "BELMONT"
    - street_type_abbr (str): An abbreviated street type. Ex: "AVE"
    - fuzziness (int): The number of addresses +/- the desired address number when searching for coordinates. The function will always return the closest address' coordinates.


    Returns:
    - Point: A Shapely point with the GPS coordinates of the address (longitude, latitude).
    """
    results = df[(address_number - fuzziness <= df['Add_Number']) &
                (df['Add_Number'] <= address_number + fuzziness) &
                (df['LSt_PreDir'] == direction_abbr.upper()) &
                (df['St_Name'] == street_name.upper()) &
                (df['LSt_Type'] == street_type_abbr.upper())].copy()

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
        print(f"Error finding coordinates for street address {address_number} {direction_abbr} {street_name} {street_type_abbr}")
        return None

    return Point(longitude, latitude)


def get_intersection_coordinates(street1: str,
                                 street2: str)-> Optional['Point']:
    """
    Return the GPS coordinates of an intersection in Chicago.

    Parameters:
    - street1 (str): A street name in Chicago. Ex: "BELMONT"
    - street2 (str): A street name in Chicago. Ex: "CLARK"

    Returns:
    - Point: A Shapely point with the GPS coordinates of the address (longitude, latitude).
    """
    if(street1 == street2):
        return None

    # select street shapes from data
    street1_data = gdf[gdf["street_nam"] == street1.upper()]
    street2_data = gdf[gdf["street_nam"] == street2.upper()]

    try:
        # join street shapes together
        street1_geometry = unary_union(street1_data['geometry'])
        street2_geometry = unary_union(street2_data['geometry'])

        intersection = street1_geometry.intersection(street2_geometry)

        if not intersection.is_empty:
            if isinstance(intersection, MultiPoint):
                # extract first point of multipoint
                ## (this tends to happen when one half of the intersecting street is offset from the other half)
                first_point = intersection.geoms[0]
                return
            if isinstance(intersection, LineString):
                first_point = intersection.coords[0]
                return first_point
            if isinstance(intersection, MultiLineString):
                first_point = intersection.geoms[0].coords[0]
                return first_point
            else:
                return intersection
        else:
            return None
    except:
        print(f"Error getting intersection coordinates for {street1} & {street2}")
        return None


'''