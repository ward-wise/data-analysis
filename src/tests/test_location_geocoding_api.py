import unittest
from chicago_participatory_urbanism.geocoder_api import GeoCoderAPI
from chicago_participatory_urbanism.ward_spending.location_geocoding import LocationGeocoder
from test_cases import address_tests

if __name__ == '__main__':

    geo_coder = GeoCoderAPI()
    for test in address_tests():
        print('---'*30)
        print(test)
        print(LocationGeocoder(geocoder=GeoCoderAPI()).process_location_text(
                text=test)
        )