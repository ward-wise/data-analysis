from unittest import mock

from shapely import LineString
from shapely.geometry import MultiPoint, Point

from src.chicago_participatory_urbanism.location_structures import (
    Intersection,
    Street,
    StreetAddress,
)
from src.chicago_participatory_urbanism.ward_spending.location_geocoding import LocationGeocoder


@mock.patch(
    "src.chicago_participatory_urbanism.ward_spending.location_geocoding.LocationGeocoder.get_geometry_from_location"
)
def test_process_location_text_single_point(mock_get_geometry_from_location):
    test_locations_txt = "point 1"
    mock_get_geometry_from_location.return_value = Point(1, 2)
    expected_result = Point(1, 2)

    test_location_geoencoder = LocationGeocoder(geocoder=mock.Mock())
    result = test_location_geoencoder.process_location_text(text=test_locations_txt)

    assert result == expected_result


@mock.patch(
    "src.chicago_participatory_urbanism.ward_spending.location_geocoding.LocationGeocoder.get_geometry_from_location"
)
def test_process_location_text_multiple_points(mock_get_geometry_from_location):
    test_locations_txt = "point 1; point 2; point 3"
    mock_get_geometry_from_location.side_effect = [Point(1, 2), Point(3, 4), Point(5, 6)]
    expected_result = MultiPoint([Point(1, 2), Point(3, 4), Point(5, 6)])

    test_location_geoencoder = LocationGeocoder(geocoder=mock.Mock())
    result = test_location_geoencoder.process_location_text(text=test_locations_txt)

    assert result == expected_result


@mock.patch("src.chicago_participatory_urbanism.ward_spending.location_geocoding.lfp")
def test_get_geometry_from_location_street_address(mock_lfp):
    mock_lfp.get_location_format.return_value = mock_lfp.LocationFormat.STREET_ADDRESS

    test_street_address = StreetAddress(
        street=Street(name="Main Street", direction="N", street_type="fake_street_type"), number=123
    )

    mock_lfp.extract_street_address.return_value = test_street_address

    mock_geoencoder = mock.Mock()
    mock_geoencoder.get_street_address_coordinates.return_value = Point(1, 2)

    test_location_geoencoder = LocationGeocoder(geocoder=mock_geoencoder)
    result = test_location_geoencoder.process_location_text(text="test_street_address")

    assert result == Point(1, 2)
    mock_geoencoder.get_street_address_coordinates.assert_called_once_with(test_street_address)


@mock.patch("src.chicago_participatory_urbanism.ward_spending.location_geocoding.lfp")
def test_get_geometry_from_location_street_address_range(mock_lfp):
    mock_lfp.get_location_format.return_value = mock_lfp.LocationFormat.STREET_ADDRESS_RANGE

    test_street_address_1 = StreetAddress(
        street=Street(name="Main Street", direction="N", street_type="fake_street_type"), number=123
    )

    test_street_address_2 = StreetAddress(
        street=Street(name="Main Street", direction="N", street_type="another_street_type"),
        number=456,
    )

    mock_lfp.extract_address_range_street_addresses.return_value = (
        test_street_address_1,
        test_street_address_2,
    )

    mock_geoencoder = mock.Mock()
    mock_geoencoder.get_street_address_coordinates.side_effect = [Point(1, 2), Point(3, 4)]

    test_location_geoencoder = LocationGeocoder(geocoder=mock_geoencoder)
    result = test_location_geoencoder.process_location_text(text="test_street_address")

    assert result == LineString([Point(1, 2), Point(3, 4)])
    mock_geoencoder.get_street_address_coordinates.assert_has_calls(
        [
            mock.call(test_street_address_1),
            mock.call(test_street_address_2),
        ],
        any_order=False,
    )


@mock.patch("src.chicago_participatory_urbanism.ward_spending.location_geocoding.lfp")
def test_get_geometry_from_location_intersection(mock_lfp):
    mock_lfp.get_location_format.return_value = mock_lfp.LocationFormat.INTERSECTION

    test_intersection = Intersection(
        street1=Street(name="Street 1", direction="N", street_type="Big"),
        street2=Street(name="Street 2", direction="", street_type="Small"),
    )

    mock_lfp.extract_intersection.return_value = test_intersection

    mock_geoencoder = mock.Mock()
    mock_geoencoder.get_intersection_coordinates.return_value = Point(1, 2)

    test_location_geoencoder = LocationGeocoder(geocoder=mock_geoencoder)
    result = test_location_geoencoder.process_location_text(text="test_intersection")

    assert result == Point(1, 2)
    mock_geoencoder.get_intersection_coordinates.assert_called_once_with(test_intersection)


@mock.patch("src.chicago_participatory_urbanism.ward_spending.location_geocoding.lfp")
def test_get_geometry_from_location_intersection(mock_lfp):

    mock_lfp.get_location_format.return_value = mock_lfp.LocationFormat.STREET_SEGMENT_INTERSECTIONS

    test_intersection = Intersection(
        street1=Street(name="Street 1", direction="N", street_type="Big"),
        street2=Street(name="Street 2", direction="", street_type="Small"),
    )

    mock_lfp.extract_intersection.return_value = test_intersection

    mock_geoencoder = mock.Mock()
    mock_geoencoder.get_intersection_coordinates.return_value = Point(1, 2)

    test_location_geoencoder = LocationGeocoder(geocoder=mock_geoencoder)
    result = test_location_geoencoder.process_location_text(text="test_intersection")

    assert result == Point(1, 2)
    mock_geoencoder.get_intersection_coordinates.assert_called_once_with(test_intersection)