import unittest
import src.chicago_participatory_urbanism.ward_spending.location_format_processing as lfp

class TestLocationFunctions(unittest.TestCase):

    # TODO make generic and add more cases
    def test_get_location_format_street_address(self):
        location = "1640 N MAPLEWOOD AVE"
        result = lfp.LocationStringProcessor(location).get_location_format([location])
        self.assertEqual(result[0]["format"], lfp.LocationFormat.STREET_ADDRESS)

    def test_extract_street_address(self):
        street_address_text = "1640 N MAPLEWOOD AVE"
        result = lfp.extract_street_address(street_address_text)
        self.assertEqual(result.number, 1640)
        self.assertEqual(result.street.direction, "N")
        self.assertEqual(result.street.name, "MAPLEWOOD")
        self.assertEqual(result.street.street_type, "AVE")

    def test_extract_segment_intersections_address_range(self):
        location = "ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)"
        result = lfp.extract_segment_intersections_address_range(location)
        self.assertEqual(result[0].number, 1200)
        self.assertEqual(result[0].street.direction, "N")
        self.assertEqual(result[0].street.name, "LEAVITT")
        self.assertEqual(result[0].street.street_type, "ST")
        self.assertEqual(result[1].number, 1600)
        self.assertEqual(result[1].street.direction, "N")
        self.assertEqual(result[1].street.name, "LEAVITT")
        self.assertEqual(result[1].street.street_type, "ST")

    def test_extract_segment_intersections(self):
        location = "ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)"
        result = lfp.extract_segment_intersections(location)
        self.assertEqual(result[0].street1.direction, "N")
        self.assertEqual(result[0].street1.name, "LEAVITT")
        self.assertEqual(result[0].street1.street_type, "ST")
        self.assertEqual(result[0].street2.direction, "W")
        self.assertEqual(result[0].street2.name, "DIVISION")
        self.assertEqual(result[0].street2.street_type, "ST")

        self.assertEqual(result[1].street1.direction, "N")
        self.assertEqual(result[1].street1.name, "LEAVITT")
        self.assertEqual(result[1].street1.street_type, "ST")
        self.assertEqual(result[1].street2.direction, "W")
        self.assertEqual(result[1].street2.name, "NORTH")
        self.assertEqual(result[1].street2.street_type, "AVE")

    # TODO
    def test_extract_alley_intersections(self):
        location = "N WOOD ST & W AUGUSTA BLVD & W CORTEZ ST & N HERMITAGE AVE"
        result = lfp.extract_alley_intersections(location)
        pass

    def test_extract_intersection_street_names(self):
        location = "N ASHLAND AVE & W CHESTNUT ST"
        result = lfp.extract_intersection(location)
        self.assertEqual(result.street1.direction, "N")
        self.assertEqual(result.street1.name, "ASHLAND")
        self.assertEqual(result.street1.street_type, "AVE")
        self.assertEqual(result.street2.direction, "W")
        self.assertEqual(result.street2.name, "CHESTNUT")
        self.assertEqual(result.street2.street_type, "ST")

    def test_extract_address_range_street_addresses(self):
        location = "434-442 E 46TH PL"
        result = lfp.extract_address_range_street_addresses(location)
        self.assertEqual(result[0].number, 434)
        self.assertEqual(result[0].street.direction, "E")
        self.assertEqual(result[0].street.name, "46TH")
        self.assertEqual(result[0].street.street_type, "PL")

        self.assertEqual(result[1].number, 442)
        self.assertEqual(result[1].street.direction, "E")
        self.assertEqual(result[1].street.name, "46TH")
        self.assertEqual(result[1].street.street_type, "PL")

    def test_extract_segment_address_intersection_info(self):
        location = "ON W 52ND PL FROM 322 W TO S PRINCETON AVE (300 W)"
        result = lfp.extract_segment_address_intersection_info(location)
        self.assertEqual(result[0].number, 322)
        self.assertEqual(result[0].street.direction, "W")
        self.assertEqual(result[0].street.name, "52ND")
        self.assertEqual(result[0].street.street_type, "PL")


        self.assertEqual(result[1].street1.name, "52ND")
        self.assertEqual(result[1].street2.name, "PRINCETON")

    def test_extract_segment_intersection_address_info(self):
        location = "ON W 52ND PL FROM S PRINCETON AVE (300 W) TO 322 W"
        result = lfp.extract_segment_intersection_address_info(location)
        self.assertEqual(result[0].street1.name, "52ND")
        self.assertEqual(result[0].street2.name, "PRINCETON")

        self.assertEqual(result[1].number, 322)
        self.assertEqual(result[1].street.direction, "W")
        self.assertEqual(result[1].street.name, "52ND")
        self.assertEqual(result[1].street.street_type, "PL")

if __name__ == '__main__':
    unittest.main()
