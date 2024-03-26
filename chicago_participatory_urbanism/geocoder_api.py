'''
This section is taking processed street addresses and
return multi_string coordinates in maps coordinates
'''
import requests
import numpy as np
from shapely.geometry import Point
from chicago_participatory_urbanism.location_structures import Intersection
from chicago_participatory_urbanism.ward_spending.location_geocoding import LocationGeocoder
import time


class GeoCoderAPI:
    # https://data.cityofchicago.org/Transportation/Street-Center-Lines/6imu-meau
    # address point csv from https://hub-cookcountyil.opendata.arcgis.com/datasets/5ec856ded93e4f85b3f6e1bc027a2472_0/about
    # https://dev.socrata.com/foundry/data.cityofchicago.org/pr57-gg9e
    # https://datacatalog.cookcountyil.gov/GIS-Maps/Cook-County-Address-Points/78yw-iddh

    'headers to query socrata api'
    api_header = {
        'Accept': 'application/json',
        # 'X-App-Token': os.getenv('app_token'),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0'
    }

    def _query_transport_api(
            self,
            params: dict,
            sql_func: str = None) -> dict:
        # https://data.cityofchicago.org/Transportation/Street-Center-Lines/6imu-meau
        # https://dev.socrata.com/foundry/data.cityofchicago.org/pr57-gg9e
        # dataset metadata : https://data.cityofchicago.org/dataset/transportation/pr57-gg9e
        # field name references: https://data.cityofchicago.org/api/assets/BD576CB8-B987-437A-ABBC-3F2CED13C26A

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

            Usage:
            without sql_function:
            self._query_transport_api(params={'street_nam': 'ARTESIAN', 'street_typ':'AVE'})

            with sql_function:
            f_cross like "%25{street_2}%25"
            self._query_transport_api(params={'street_nam': 'ARTESIAN', 'street_typ':'AVE'},
                                      sql_func='f_cross like "%2568TH%25"')
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
        else:
            link = base_link + query_params

        resp = requests.get(link, headers=self.api_header)

        # when json response is empty list or error message
        if (len(resp.json()) == 0) or (isinstance(resp.json(), dict)):
            return None
        else:
            coordinate = resp.json()[0]['the_geom']['coordinates']
            return np.array(coordinate).reshape(-1, 2)[0]

    def _query_address_api(
            self,
            params: dict,
            sql_func: str = None) -> dict:
        '''
        useful fields:
        "Add_Number"-address number
        "st_name"
        "cmpaddabrv"

        Usage:
        without sql_function:
        self._query_transport_api(params={'street_nam': 'ARTESIAN', 'street_typ':'AVE'})

        with sql_function:
        f_cross like "%25{street_2}%25"
        self._query_transport_api(params={'street_nam': 'ARTESIAN', 'street_typ':'AVE'},
                                  sql_func='f_cross like "%2568TH%25"')
        '''
        base_link = 'https://datacatalog.cookcountyil.gov/resource/78yw-iddh.json?$where='
        query_params = ' AND '.join(k + ' like ' + "'"+str(v).upper() + "'"
                                    for k, v in params.items())

        if sql_func is not None:
            sql_func_string = 'AND ' + sql_func
            link = base_link + query_params + sql_func_string
        else:
            link = base_link + query_params

        resp = requests.get(link, headers=self.api_header)
        # when json response is empty list or error message
        if (len(resp.json()) == 0) or (isinstance(resp.json(), dict)):
            return None
        else:
            coordinate = resp.json()[0]['the_geom']['coordinates']
            return np.array(coordinate).reshape(-1, 2)

    def _query_nominatim(self, query_string) -> dict:
        '''
        rate limit of 1 request per second,
        example - 200 E 40TH ST
        https://nominatim.openstreetmap.org/search?q=200 E 40TH ST chicago il&format=jsonv2
        '''
        time.sleep(1)
        query_string = query_string + ', chicago il'

        query_link = f'https://nominatim.openstreetmap.org/search?q={query_string}&format=jsonv2'

        resp = requests.get(query_link, headers=self.api_header)


        # if return empty list
        if len(resp.json())==0:
            return None
        else:
            coordinate = np.array(
                            [float(resp.json()[0]['lon']),
                            float(resp.json()[0]['lat'])]
                        )
            return coordinate

    def _query_census_api(self, query_string):
        '''
        TO DO:
        switch openstreetmap with US Census geocoder: https://geocoding.geo.census.gov/geocoder/
        example:
        https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address=4600+Silver+Hill+Rd%2C+Washington%2C+DC+20233&benchmark=2020&format=json
        https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address=1244%20N%20ASHLAND%20AVE%2C%20Chicago%20IL&benchmark=4

        for Alley: replce "&" with "%26" in query string

        Usage:
        self._query_census_api("W DIVISION ST & N PAULINA ST")
        self._query_census_api("3221 W ARMITAGE AVE")

        '''
        query_string = query_string.replace('&', '%26').replace(' ', '%20')

        query_link = f'https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address={query_string}%2C%20Chicago%20IL&benchmark=4'


        resp = requests.get(query_link, headers=self.api_header)

        street_match = resp.json()['result']['addressMatches']

        # 'addressMatches' field is an empty list
        if len(street_match)==0:
            return None
        else:
            coord = resp.json()['result']['addressMatches'][0]['coordinates']

            coordinates = np.array(
                [float(coord['x']),
                 float(coord['y'])]
            )

        return coordinates

    def get_street_address_coordinates(
            self,
            address: str) -> Point:
        # get_street_address_coordinates_from_full_name
        '''
        run address string to APIs until a match, or return None
        Return the GPS coordinates of a street address in Chicago.

        :Parameters:
        - StreetAddress
        example: StreetAddress(number=50, street=Street(direction='W', name='125TH', street_type='PL')

        :Returns:
        - Point: A Shapely point with the GPS coordinates of the address (longitude, latitude).
        '''
        results = self._query_address_api(
            params={'cmpaddabrv': str(address).upper()}
        )
        if results is not None and results.any():
            return Point(results)

        results = self._query_census_api(
            query_string=str(address).upper()
        )
        if results is not None and results.any():
            return Point(results)

        results = self._query_nominatim(
                query_string=str(address).upper()
        )
        if results is not None and results.any():
            return Point(results)
        else:
            return None

    def get_intersection_coordinates(
            self,
            intersection: Intersection) -> Point:
        """
        Return the GPS coordinates of an intersection in Chicago.

        Parameters:
        - Intersection
        example: Intersection(street1=Street(direction='', name='WELLINGTON', street_type='')
                              street2=Street(direction='', name='WELLINGTON', street_type=''))

        Returns:
        - Point: A Shapely point with the GPS coordinates of the address (longitude, latitude).
        """
        street_1 = intersection.street1.name
        street_2 = intersection.street2.name

        result = self._query_transport_api(
                params={'street_nam': street_1},
                sql_func=f'f_cross like "%25{street_2}%25"'
        )
        if result is not None and result.any():
            return Point(result)

        result = self._query_transport_api(
                params={'street_nam': street_2},
                sql_func=f't_cross like "%25{street_1}%25"'
        )
        if result is not None and result.any():
            return Point(result)

        result = self._query_census_api(
            query_string=f'{street_1} AND {street_2}'
        )
        if result is not None and result.any():
            return Point(result)

if __name__ == '__main__':

    coder = LocationGeocoder(geocoder=GeoCoderAPI())
    print(coder.process_location_text('ON W EVERGREEN AVE FROM N MILWAUKEE AVE  (1800 W) TO W SCHILLER ST  (1900 W)'))

    # ARTESIAN
    # 3221 W ARMITAGE AVE
    # print(GeoCoderAPI().get_street_address_coordinates_from_full_name(address='SURF'))
    # cross = Intersection(street1='W DIVISION ST', street2='N PAULINA ST')
    # print(GeoCoderAPI().get_intersection_coordinates(intersection=cross))