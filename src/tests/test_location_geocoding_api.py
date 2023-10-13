import unittest
from chicago_participatory_urbanism.geocoder_api import GeoCoderAPI
from chicago_participatory_urbanism.ward_spending.location_geocoding import LocationGeocoder
from cases import address_tests

class TestGeocoderAPI(unittest.TestCase):

    # TODO make generic and add more cases
    def test_geocoder_API_initialization(self):
        geo_coder = GeoCoderAPI()
        self.assertIsInstance(geo_coder, GeoCoderAPI, "Object is not an instance of GeoCodeAPI")


# TODO needs to be converted to work with unittest framework
def run_geocoder_api():
    geo_coder = GeoCoderAPI()
    for test in address_tests():
        print('---'*30)
        print(test)
        print(LocationGeocoder(geocoder=GeoCoderAPI()).process_location_text(
                text=test)
        )

if __name__ == '__main__':
    unittest.main()