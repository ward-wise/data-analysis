import src.chicago_participatory_urbanism.ward_spending.location_format_processing as lfp

# TODO make generic and add more cases
def test_get_location_format_street_address():
    location = "1640 N MAPLEWOOD AVE"
    result = lfp.LocationStringProcessor(location).get_location_format([location])
    assert result[0]["format"] == lfp.LocationFormat.STREET_ADDRESS

def test_extract_street_address():
    street_address_text = "1640 N MAPLEWOOD AVE"
    result = lfp.extract_street_address(street_address_text)
    assert result.number == 1640
    assert result.street.direction == "N"
    assert result.street.name == "MAPLEWOOD"
    assert result.street.street_type == "AVE"

def test_extract_segment_intersections_address_range():
    location = "ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)"
    result = lfp.extract_segment_intersections_address_range(location)
    assert result[0].number == 1200
    assert result[0].street.direction == "N"
    assert result[0].street.name == "LEAVITT"
    assert result[0].street.street_type == "ST"
    assert result[1].number == 1600
    assert result[1].street.direction == "N"
    assert result[1].street.name == "LEAVITT"
    assert result[1].street.street_type == "ST"

def test_extract_segment_intersections():
    location = "ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)"
    result = lfp.extract_segment_intersections(location)
    assert result[0].street1.direction == "N"
    assert result[0].street1.name == "LEAVITT"
    assert result[0].street1.street_type == "ST"
    assert result[0].street2.direction == "W"
    assert result[0].street2.name == "DIVISION"
    assert result[0].street2.street_type == "ST"

    assert result[1].street1.direction == "N"
    assert result[1].street1.name == "LEAVITT"
    assert result[1].street1.street_type == "ST"
    assert result[1].street2.direction == "W"
    assert result[1].street2.name == "NORTH"
    assert result[1].street2.street_type == "AVE"

# TODO
def test_extract_alley_intersections():
    location = "N WOOD ST & W AUGUSTA BLVD & W CORTEZ ST & N HERMITAGE AVE"
    result = lfp.extract_alley_intersections(location)
    pass

def test_extract_intersection_street_names():
    location = "N ASHLAND AVE & W CHESTNUT ST"
    result = lfp.extract_intersection(location)
    assert result.street1.direction == "N"
    assert result.street1.name == "ASHLAND"
    assert result.street1.street_type == "AVE"
    assert result.street2.direction == "W"
    assert result.street2.name == "CHESTNUT"
    assert result.street2.street_type == "ST"

def test_extract_address_range_street_addresses():
    location = "434-442 E 46TH PL"
    result = lfp.extract_address_range_street_addresses(location)
    assert result[0].number == 434
    assert result[0].street.direction == "E"
    assert result[0].street.name == "46TH"
    assert result[0].street.street_type == "PL"

    assert result[1].number == 442
    assert result[1].street.direction == "E"
    assert result[1].street.name == "46TH"
    assert result[1].street.street_type == "PL"

def test_extract_segment_address_intersection_info():
    location = "ON W 52ND PL FROM 322 W TO S PRINCETON AVE (300 W)"
    result = lfp.extract_segment_address_intersection_info(location)
    assert result[0].number == 322
    assert result[0].street.direction == "W"
    assert result[0].street.name == "52ND"
    assert result[0].street.street_type == "PL"


    assert result[1].street1.name == "52ND"
    assert result[1].street2.name == "PRINCETON"

def test_extract_segment_intersection_address_info():
    location = "ON W 52ND PL FROM S PRINCETON AVE (300 W) TO 322 W"
    result = lfp.extract_segment_intersection_address_info(location)
    assert result[0].street1.name == "52ND"
    assert result[0].street2.name == "PRINCETON"

    assert result[1].number == 322
    assert result[1].street.direction == "W"
    assert result[1].street.name == "52ND"
    assert result[1].street.street_type == "PL"
