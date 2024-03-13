import itertools

import pytest

from src.chicago_participatory_urbanism.location_structures import (
    Intersection,
    Street,
    StreetAddress,
)
from src.chicago_participatory_urbanism.ward_spending.location_format_processing import (
    LocationFormat,
    extract_address_range_street_addresses,
    extract_alley_intersections,
    extract_intersection,
    extract_segment_address_intersection_info,
    extract_segment_intersection_address_info,
    extract_segment_intersections,
    extract_street_address,
    get_location_format,
)


@pytest.mark.parametrize(
    "test_location, expected_format",
    [
        ("1640 N MAPLEWOOD AVE", LocationFormat.STREET_ADDRESS),
        (
            "ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)",
            LocationFormat.STREET_SEGMENT_INTERSECTIONS,
        ),
        ("N WOOD ST & W AUGUSTA BLVD & W CORTEZ ST & N HERMITAGE AVE", LocationFormat.ALLEY),
        ("N ASHLAND AVE & W CHESTNUT ST", LocationFormat.INTERSECTION),
        ("434-442 E 46TH PL", LocationFormat.STREET_ADDRESS_RANGE),
        (
            "ON W 52ND PL FROM 322 W TO S PRINCETON AVE (300 W)",
            LocationFormat.STREET_SEGMENT_ADDRESS_INTERSECTION,
        ),
        (
            "ON W 52ND PL FROM S PRINCETON AVE (300 W) TO 322 W",
            LocationFormat.STREET_SEGMENT_INTERSECTION_ADDRESS,
        ),
        (
            "NOT A LOCATION",
            LocationFormat.UNIDENTIFIED,
        ),
    ],
)
def test_get_location_format(test_location: str, expected_format: LocationFormat):
    assert get_location_format(test_location) == expected_format


def test_extract_street_address():
    street_address_text = "1640 N MAPLEWOOD AVE"
    result = extract_street_address(street_address_text)

    assert result == StreetAddress(
        number=1640,
        street=Street(direction="N", name="MAPLEWOOD", street_type="AVE"),
    )


def test_extract_segment_intersections():
    location = "ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)"
    result = extract_segment_intersections(location)

    assert result[0] == Intersection(
        street1=Street(direction="N", name="LEAVITT", street_type="ST"),
        street2=Street(direction="W", name="DIVISION", street_type="ST"),
    )

    assert result[1] == Intersection(
        street1=Street(direction="N", name="LEAVITT", street_type="ST"),
        street2=Street(direction="W", name="NORTH", street_type="AVE"),
    )


# TODO: make test more strict
def test_extract_alley_intersections():
    location = "N WOOD ST & W AUGUSTA BLVD & W CORTEZ ST & N HERMITAGE AVE"
    result = extract_alley_intersections(location)

    assert len(result) == 6

    street1 = Street(direction="N", name="WOOD", street_type="ST")
    street2 = Street(direction="W", name="AUGUSTA", street_type="BLVD")
    street3 = Street(direction="W", name="CORTEZ", street_type="ST")
    street4 = Street(direction="N", name="HERMITAGE", street_type="AVE")

    for subset in itertools.combinations([street1, street2, street3, street4], 2):
        assert (
            Intersection(street1=subset[0], street2=subset[1]) in result
            or Intersection(street1=subset[1], street2=subset[0]) in result
        )


def test_extract_intersection_street_names():
    location = "N ASHLAND AVE & W CHESTNUT ST"
    result = extract_intersection(location)
    assert result == Intersection(
        street1=Street(direction="N", name="ASHLAND", street_type="AVE"),
        street2=Street(direction="W", name="CHESTNUT", street_type="ST"),
    )


def test_extract_address_range_street_addresses():
    location = "434-442 E 46TH PL"
    result = extract_address_range_street_addresses(location)

    assert result[0] == StreetAddress(
        number=434,
        street=Street(direction="E", name="46TH", street_type="PL"),
    )

    assert result[1] == StreetAddress(
        number=442, street=Street(direction="E", name="46TH", street_type="PL")
    )


def test_extract_segment_address_intersection_info():
    location = "ON W 52ND PL FROM 322 W TO S PRINCETON AVE (300 W)"
    result = extract_segment_address_intersection_info(location)

    assert result[0] == StreetAddress(
        number=322, street=Street(direction="W", name="52ND", street_type="PL")
    )

    assert result[1] == Intersection(
        street1=Street(direction="W", name="52ND", street_type="PL"),
        street2=Street(direction="S", name="PRINCETON", street_type="AVE"),
    )


def test_extract_segment_intersection_address_info():
    location = "ON W 52ND PL FROM S PRINCETON AVE (300 W) TO 322 W"
    result = extract_segment_intersection_address_info(location)

    assert result[0] == Intersection(
        street1=Street(direction="W", name="52ND", street_type="PL"),
        street2=Street(direction="S", name="PRINCETON", street_type="AVE"),
    )

    assert result[1] == StreetAddress(
        number=322, street=Street(direction="W", name="52ND", street_type="PL")
    )
