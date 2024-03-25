'''
This section is taking processed street addresses and
return multi_string coordinates in maps coordinates
'''
from typing import TypedDict
import os
import requests
import numpy as np
from shapely.geometry import Point
from src.chicago_participatory_urbanism.location_structures import StreetAddress, Intersection
import time

class GeoCoderAPI:
    # https://data.cityofchicago.org/Transportation/Street-Center-Lines/6imu-meau
    # address point csv from https://hub-cookcountyil.opendata.arcgis.com/datasets/5ec856ded93e4f85b3f6e1bc027a2472_0/about
    # https://dev.socrata.com/foundry/data.cityofchicago.org/pr57-gg9e
    # https://datacatalog.cookcountyil.gov/GIS-Maps/Cook-County-Address-Points/78yw-iddh

    'headers to query socrata api'
    api_header = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0'
    }

    def _query_transport_api(
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
        resp.raise_for_status()

        return resp.json()

    def _query_address_api(
            self,
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
        resp.raise_for_status()

        return resp.json()

    def _query_nominatim(self, query_string) -> TypedDict:
        '''
        rate limit of 1 request per second,
        example - 200 E 40TH ST
        https://nominatim.openstreetmap.org/search?q=200 E 40TH ST chicago il&format=jsonv2
        '''
        time.sleep(1)
        nom_header = self.api_header.copy()
        nom_header.pop('X-App-Token')
        query_string = query_string + ', chicago il'

        query_link = f'https://nominatim.openstreetmap.org/search?q={query_string}&format=jsonv2'

        resp = requests.get(query_link, headers=nom_header)
        resp.raise_for_status()

        return resp.json()

    def get_street_address_coordinates_from_full_name(
            self,
            address: str) -> Point:
        coors = []
        try:
            results = self._query_address_api(
                params={'cmpaddabrv': str(address).upper()})
            _coordinate = tuple(
                np.array(results[0]['the_geom']['coordinates']).reshape(-1, 2)[0])
            coors.append(_coordinate)

        except IndexError:
            'if API return empty'
            results = self._query_nominatim(
                query_string=str(address).upper()
            )
            if results:
                _coordinate = (float(results[0]['lon']), float(results[0]['lat']))
                coors.append(_coordinate)
            else:
                return None

        except KeyError:
            return None

        return Point(coors)

    def get_street_address_coordinates(
            self,
            address: StreetAddress,
            fuzziness: int = 10) -> Point:
        """
        Return the GPS coordinates of a street address in Chicago.

        :Parameters:
        - StreetAddress
        example: StreetAddress(number=50, street=Street(direction='W', name='125TH', street_type='PL')

        :Returns:
        - Point: A Shapely point with the GPS coordinates of the address (longitude, latitude).
        """
        coors = []
        try:
            results = self._query_address_api(
                params={'cmpaddabrv': str(address).upper()}
            )
            _coordinate = tuple(
                np.array(results[0]['the_geom']['coordinates']).reshape(-1, 2)[0])
            coors.append(_coordinate)

        except IndexError:
            "if API return empty"
            results = self._query_nominatim(
                query_string=str(address).upper()
            )
            if results:
                _coordinate = (float(results[0]['lon']), float(results[0]['lat']))
                coors.append(_coordinate)
            else:
                return None

        except KeyError:
            return None

        return Point(coors)

    def get_intersection_coordinates(
            self,
            intersection: Intersection) -> Point:
        """
        Return the GPS coordinates of an intersection in Chicago.

        Parameters:
        - Intersection
        example: Intersection(street1=Street(direction='', name='WELLINGTON', street_type='')

        Returns:
        - Point: A Shapely point with the GPS coordinates of the address (longitude, latitude).
        """
        street_1 = intersection.street1.name
        street_2 = intersection.street2.name
        corner = ()
        try:
            result = self._query_transport_api(
                params={'street_nam': street_1},
                sql_func=f'f_cross like "%25{street_2}%25"'
            )
            _coordinate = tuple(
                np.array(result[0]['the_geom']['coordinates']).reshape(-1, 2)[0]
            )
            if result:
                corner = _coordinate

        except IndexError:
            result = self._query_transport_api(
                params={'street_nam': street_2},
                sql_func=f't_cross like "%25{street_1}%25"'
            )
            if result:
                _coordinate = tuple(
                    np.array(result[0]['the_geom']['coordinates']).reshape(-1, 2)[0]
                )
                corner = _coordinate
            else:
                return None

        return Point(corner)
