'''
This section is taking processed street addresses and
return multi_string coordinates in maps coordinates
'''
from typing import Any, TypedDict
import os
import requests
import numpy as np
from dotenv import load_dotenv
from itertools import combinations
from address_format_processing import LocationFormat, LocationStringProcessor
import time


load_dotenv()


class GeoCoder:
    # https://data.cityofchicago.org/Transportation/Street-Center-Lines/6imu-meau
    # address point csv from https://hub-cookcountyil.opendata.arcgis.com/datasets/5ec856ded93e4f85b3f6e1bc027a2472_0/about
    # https://dev.socrata.com/foundry/data.cityofchicago.org/pr57-gg9e
    # https://datacatalog.cookcountyil.gov/GIS-Maps/Cook-County-Address-Points/78yw-iddh

    'headers to query socrata api'
    api_header = {
        'Accept': 'application/json',
        'X-App-Token': os.getenv('app_token'),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0'
    }

    def __init__(self,
                 add_string: str = None,
                 add_processor: Any = LocationStringProcessor,
                 ) -> None:
        # location strings and text processor
        self.address_string: str = add_string
        self.processor: Any = add_processor
        # variable to track street names and format type return by processor
        self.streets: str = None
        self.format: Any = None
        # variable to keep track of coordinates return by API
        self.coors: list = []

        if self.address_string is not None:
            self.run_processor()

    def run_processor(self) -> 'GeoCoder':
        'run street text processor'

        processing = (
            self.processor(location_string=self.address_string).run())

        self.streets = processing['proc_string']
        self.format = processing['format']
        return self

    def query_transport_api(
            self,
            params: dict,
            sql_func: str = None) -> TypedDict:
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
        time.sleep(0.1)
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

    def query_address_api(self,
                          params: dict,
                          sql_func: str = None) -> TypedDict:
        '''
        useful fields:
        "Add_Number"-address number
        "st_name"
        "cmpaddabrv"
        '''
        time.sleep(0.1)

        base_link = 'https://datacatalog.cookcountyil.gov/resource/78yw-iddh.json?$where='
        query_params = ' AND '.join(k + ' like ' + "'"+str(v).upper() + "'"
                                    for k, v in params.items())

        if sql_func is not None:
            sql_func_string = 'AND ' + sql_func
            link = base_link + query_params + sql_func_string
            resp = requests.get(link, headers=self.api_header)
            return resp.json()

        link = base_link + query_params
        resp = requests.get(link, headers=self.api_header)

        return resp.json()

    def query_nominatim(self, query_string) -> TypedDict:
        '''
        rate limit of 1 request per second,
        example - 200 E 40TH ST
        https://nominatim.openstreetmap.org/search?q=200 E 40TH ST chicago il&format=jsonv2
        '''
        time.sleep(1)
        user_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0'
        }
        query_string = query_string + ' chicago il'

        query_link = f'https://nominatim.openstreetmap.org/search?q={query_string}&format=jsonv2'

        resp = requests.get(query_link, headers=user_header)

        return resp.json()

    def find_intersections(self) -> 'GeoCoder':
        '''
        should be use for format type:
        -LocationFormat.INTERSECTION
        -LocationFormat.STREET_SEGMENT_INTERSECTIONS
        '''
        match len(self.streets):
            case 2:
                'in case of 2 streets, it is intersection'
                street_1, street_2 = self.streets

                results = self.query_transport_api(
                                params={'street_nam': street_1},
                                sql_func=f'f_cross like "%25{street_2}%25"')
                # reshape nested lists
                _coordinate = list(np.array(results[0]['the_geom']['coordinates']).reshape(-1, 2)[0])
                self.coors.append(_coordinate)
                return self

            case 3:
                'in case of 3, section between two streets, should be a line'
                street_1, street_2, street_3 = self.streets

                for st in street_2, street_3:
                    try:
                        results = self.query_transport_api(
                                    params={'street_nam': street_1},
                                    sql_func=f'f_cross like "%25{st}%25"')
                        _coordinate = list(
                            np.array(results[0]['the_geom']['coordinates']).reshape(-1, 2)[0]
                        )
                    except IndexError:
                        'if returned results is empty'
                        results = self.query_transport_api(
                            params={'street_nam': street_1},
                            sql_func=f't_cross like "%25{st}%25"'
                        )
                        # should be appending the last coordinate instead of first
                        _coordinate = list(
                            np.array(results[0]['the_geom']['coordinates']).reshape(-1, 2)[-1]
                        )
                    self.coors.append(_coordinate)
                return self

    def find_alley(self) -> 'GeoCoder':
        'use for LocationFormat.ALLEY'
        '''
        example: ('WOOD', 'AUGUSTA', 'CORTEZ', 'HERMITAGE')
        pairs ('WOOD', 'AUGUSTA'), ('WOOD', 'CORTEZ'),
        ('HERMITAGE', 'AUGUSTA'), ('HERMITAGE', 'CORTEZ')
        '''
        if len(self.streets) < 4:
            raise ValueError('need 4 streets for alley')

        # make pairs of unique combinations
        make_pairs = list(combinations(self.streets, 2))
        corners = set()
        for pair in make_pairs:
            try:
                results = self.query_transport_api(
                    params={'street_nam': pair[0]},
                    sql_func=f'f_cross like "%25{pair[1]}%25"')
                _coordinate = tuple(
                    np.array(results[0]['the_geom']['coordinates']).reshape(-1, 2)[0]
                )
                corners.add(_coordinate)
            except IndexError:
                "returned nothing from API, maybe streets don't cross"
                continue

        self.coors = list(corners)
        return self

    def find_address(self) -> 'GeoCoder':
        # match type of self.streets
        # single address -> type string of actual address
        # more address -> type tuple with 2 address
        match self.streets:

            case str():
                try:
                    results = self.query_address_api(
                        params={'cmpaddabrv': str(self.streets).upper()})

                    _coordinate = list(
                        np.array(results[0]['the_geom']['coordinates']).reshape(-1, 2)[0])
                    self.coors.append(_coordinate)

                except IndexError:
                    'if API return empty'
                    results = self.query_nominatim(
                        query_string=str(self.streets).upper()
                    )
                    _coordinate = (float(results[0]['lon']), float(results[0]['lat']))
                    self.coors.append(_coordinate)
                return self

            case tuple():
                for st in self.streets:
                    try:
                        results = self.query_address_api(
                            params={'cmpaddabrv': str(st).upper()})

                        _coordinate = list(
                            np.array(results[0]['the_geom']['coordinates']).reshape(-1, 2)[0])
                        self.coors.append(_coordinate)

                    except IndexError:
                        'if API return empty'
                        results = self.query_nominatim(
                            query_string=str(st).upper()
                        )
                        _coordinate = (float(results[0]['lon']), float(results[0]['lat']))
                        self.coors.append(_coordinate)
                return self

        return self

    def find_address_to_intersection(self) -> 'GeoCoder':
        '''
        two parts:
        1- find point address
        2- find intersection
        '''
        # find point address
        try:
            results = self.query_address_api(
                params={'cmpaddabrv': str(self.streets[0]).upper()})

            _coordinate = list(
                np.array(results[0]['the_geom']['coordinates']).reshape(-1, 2)[0])
            self.coors.append(_coordinate)

        except IndexError:
            'if API return empty'
            results = self.query_nominatim(
                query_string=str(self.streets).upper()
            )
            _coordinate = (float(results[0]['lon']), float(results[0]['lat']))
            self.coors.append(_coordinate)

        'in case of 2 streets, it is intersection'
        street_1, street_2 = (self.streets[1], self.streets[2])

        results = self.query_transport_api(
                        params={'street_nam': street_1},
                        sql_func=f'f_cross like "%25{street_2}%25"')
        # reshape nested lists
        _coordinate = list(np.array(results[0]['the_geom']['coordinates']).reshape(-1, 2)[0])
        self.coors.append(_coordinate)

        return self

    def run(self) -> list:
        'run coordinate finder and return a list of coordinates'

        if ((self.format == LocationFormat.INTERSECTION) or
                (self.format == LocationFormat.STREET_SEGMENT_INTERSECTIONS)):

            self.find_intersections()
            return self.coors

        elif self.format == LocationFormat.STREET_SEGMENT_ADDRESS_INTERSECTION:

            self.find_address_to_intersection()
            return self.coors

        elif self.format == LocationFormat.ALLEY:

            self.find_alley()
            return self.coors

        elif ((self.format == LocationFormat.STREET_ADDRESS) or
                (self.format == LocationFormat.STREET_ADDRESS_RANGE)):

            self.find_address()
            return self.coors


if __name__ == '__main__':
    loc_1 = 'ON N RIDGEWAY AVE FROM W SCHOOL ST (3300 N) TO W BELMONT AVE (3200 N)'
    loc_2 = 'N MILWAUKEE AVE & N WASHTENAW AVE'
    loc_3 = '5300-5330 S PRAIRIE AVE'
    loc_4 = 'ON W 70TH ST FROM S GREEN ST (830 W) TO S PEORIA ST (900 W)'
    loc_5 = '434-442 E 46TH PL'  # unable to find address in address API
    loc_6 = 'S DORCHESTER AVE & E MADISON PARK  & S WOODLAWN AVE & E 50TH ST'  # shouldn't be intersection, should be alley
    loc_7 = 'ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)'
    loc_8 = 'N WOOD ST & W AUGUSTA BLVD & W CORTEZ ST & N HERMITAGE AVE'
    loc_9 = 'ON W 52ND PL FROM 322 W TO S PRINCETON AVE (300 W)'  #
    loc_10 = '3221 W ARMITAGE AVE'
    loc_11 = 'ON N KOLMAR AVE FROM W CORNELIA AVE (3500 N) TO W ADDISON ST (3600 N)'
    loc_12 = '200-250 E 40TH ST'  # unable to find addresss
    loc_13 = 'N WHIPPLE ST & W BLOOMINGDALE AVE & N HUMBOLDT BLVD W & W CORTLAND ST'

    test_case = loc_13
    print(GeoCoder(
            test_case,
            ).format)
    print(GeoCoder(
            add_string=test_case
            ).streets)
    print(GeoCoder(
        add_string=test_case).run()
    )
