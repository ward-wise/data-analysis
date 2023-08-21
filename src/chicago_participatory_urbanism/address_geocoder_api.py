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
                 address_string: str = None,
                 address_format: Any = LocationFormat,
                 ) -> None:
        # location strings and text processor
        self.address_string: str = address_string
        self.address_format: Any = address_format
        # variable to keep track of coordinates return by API
        self.coors: list = []

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
        nom_header = self.api_header.copy()
        nom_header.pop('X-App-Token')
        query_string = query_string + ' chicago il'

        query_link = f'https://nominatim.openstreetmap.org/search?q={query_string}&format=jsonv2'

        resp = requests.get(query_link, headers=nom_header)

        return resp.json()

    def find_intersections(self) -> 'GeoCoder':
        '''
        should be use for format type:
        -LocationFormat.INTERSECTION
        -LocationFormat.STREET_SEGMENT_INTERSECTIONS
        '''
        match len(self.address_string):
            case 2:
                'in case of 2 streets, it is intersection'
                street_1, street_2 = self.address_string
                try:
                    results = self.query_transport_api(
                                    params={'street_nam': street_1},
                                    sql_func=f'f_cross like "%25{street_2}%25"')
                    # reshape nested lists

                    _coordinate = tuple(np.array(results[0]['the_geom']['coordinates']).reshape(-1, 2)[0])

                except IndexError:
                    results = self.query_transport_api(
                                    params={'street_nam': street_1},
                                    sql_func=f't_cross like "%25{street_2}%25"')
                    # reshape nested lists

                    _coordinate = tuple(np.array(results[0]['the_geom']['coordinates']).reshape(-1, 2)[0])

                self.coors.append(_coordinate)
                return self

            case 3:
                'in case of 3, section between two streets, should be a line'
                street_1, street_2, street_3 = self.address_string

                for st in street_2, street_3:
                    try:
                        results = self.query_transport_api(
                                    params={'street_nam': street_1},
                                    sql_func=f'f_cross like "%25{st}%25"')
                        _coordinate = tuple(
                            np.array(results[0]['the_geom']['coordinates']).reshape(-1, 2)[0]
                        )
                    except IndexError:
                        'if returned results is empty'
                        results = self.query_transport_api(
                            params={'street_nam': street_1},
                            sql_func=f't_cross like "%25{st}%25"'
                        )
                        if len(results) != 0:
                            # should be appending the last coordinate instead of first
                            _coordinate = tuple(
                                np.array(results[0]['the_geom']['coordinates']).reshape(-1, 2)[-1]
                            )
                        else:
                            _coordinate = None

                    self.coors.append(_coordinate)
                return self

    def find_alley(self) -> 'GeoCoder':
        'use for LocationFormat.ALLEY'
        '''
        example: ('WOOD', 'AUGUSTA', 'CORTEZ', 'HERMITAGE')
        pairs ('WOOD', 'AUGUSTA'), ('WOOD', 'CORTEZ'),
        ('HERMITAGE', 'AUGUSTA'), ('HERMITAGE', 'CORTEZ')
        '''
        if len(self.address_string) < 4:
            raise ValueError('need 4 streets for alley')

        # make pairs of unique combinations
        make_pairs = list(combinations(self.address_string, 2))
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
        # match type of self.address_string
        # single address -> type string of actual address
        # more address -> type tuple with 2 address
        match self.address_string:

            case str():
                try:
                    results = self.query_address_api(
                        params={'cmpaddabrv': str(self.address_string).upper()})
                    _coordinate = tuple(
                        np.array(results[0]['the_geom']['coordinates']).reshape(-1, 2)[0])
                    self.coors.append(_coordinate)

                    return self

                except IndexError:
                    'if API return empty'
                    results = self.query_nominatim(
                        query_string=str(self.address_string).upper()
                    )
                    if results:
                        _coordinate = (float(results[0]['lon']), float(results[0]['lat']))
                        self.coors.append(_coordinate)
                    else:
                        self.coors = None

                    return self

                except KeyError:
                    self.coors = None

                return self

            case tuple():
                for st in self.address_string:
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
                params={'cmpaddabrv': str(self.address_string[0]).upper()})

            _coordinate = tuple(
                np.array(results[0]['the_geom']['coordinates']).reshape(-1, 2)[0])
            self.coors.append(_coordinate)

        except IndexError:
            'if API return empty'
            results = self.query_nominatim(
                query_string=str(self.address_string).upper()
            )
            _coordinate = tuple(float(results[0]['lon']), float(results[0]['lat']))
            self.coors.append(_coordinate)

        'in case of 2 streets, it is intersection'
        street_1, street_2 = (self.address_string[1], self.address_string[2])

        results = self.query_transport_api(
                        params={'street_nam': street_1},
                        sql_func=f'f_cross like "%25{street_2}%25"')
        # reshape nested lists
        _coordinate = tuple(np.array(results[0]['the_geom']['coordinates']).reshape(-1, 2)[0])
        self.coors.append(_coordinate)

        return self

    def run(self) -> list:
        'run coordinate finder and return a list of coordinates'

        if ((self.address_format == LocationFormat.INTERSECTION) or
                (self.address_format == LocationFormat.STREET_SEGMENT_INTERSECTIONS)):

            self.find_intersections()
            return self.coors

        elif self.address_format == LocationFormat.STREET_SEGMENT_ADDRESS_INTERSECTION:

            self.find_address_to_intersection()
            return self.coors

        elif self.address_format == LocationFormat.ALLEY:

            self.find_alley()
            return self.coors

        elif ((self.address_format == LocationFormat.STREET_ADDRESS) or
                (self.address_format == LocationFormat.STREET_ADDRESS_RANGE)):

            self.find_address()
            return self.coors

        elif self.address_format == LocationFormat.UNIDENTIFY:

            self.coors = None
            return self.coors
        else:

            self.coors = None
            return self.coors


def run_geocoder(addresses):

    # return format: list[dict['format'], dict['proc_string']]
    formatted_addresses = LocationStringProcessor(addresses).run()
    coordinate = []
    for address in formatted_addresses:
        coord = GeoCoder(
            address_string=address['proc_string'],
            address_format=address['format']
        ).run()
        coordinate.append(coord)

    return coordinate


if __name__ == '__main__':
    from tests.test_cases import add_tests

    for test in add_tests():
        print('---'*25)
        print(test)
        print(run_geocoder(test))
