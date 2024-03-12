from src.chicago_participatory_urbanism.geocoder_api import GeoCoderAPI
from src.chicago_participatory_urbanism.ward_spending.location_geocoding import (
    LocationGeocoder,
)

from shapely import geometry, Point, MultiPoint, LineString, Polygon, GeometryCollection

import pytest


def test_geocoder_api_initialization(monkeypatch):
    monkeypatch.setenv("app_token", "fake_app_token")
    geo_coder = GeoCoderAPI()

    assert type(geo_coder) is GeoCoderAPI
    assert geo_coder.api_header["X-App-Token"] == "fake_app_token"


@pytest.mark.parametrize(
    "test_location, expected_result_type",
    [
        (
            "ON N RIDGEWAY AVE FROM W SCHOOL ST (3300 N) TO W BELMONT AVE (3200 N)",
            LineString,
        ),
        ("N MILWAUKEE AVE & N WASHTENAW AVE", Point),
        ("1110 N STATE ST; 1030 N STATE ST", MultiPoint),
        ("5300-5330 S PRAIRIE AVE", LineString),
        ("ON W 70TH ST FROM S GREEN ST (830 W) TO S PEORIA ST (900 W)", LineString),
        ("434-442 E 46TH PL", LineString),  # unable to find address in address API
        ("S DORCHESTER AVE & E MADISON PARK  & S WOODLAWN AVE & E 50TH ST", Polygon),
        (
            "ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)",
            LineString,
        ),
        ("N WOOD AVE & W AUGUSTA ST & W CORTEZ ST & N HERMITAGE AVE", Polygon),
        ("ON W 52ND PL FROM 322 W TO S PRINCETON AVE (300 W)", LineString),
        ("3221 W ARMITAGE AVE", Point),
        ("N CAMPBELL AVE & W LE MOYNE ST & W HIRSCH ST & N MAPLEWOOD AVE", Polygon),
        (
            "ON N KOLMAR AVE FROM W CORNELIA AVE (3500 N) TO W ADDISON ST (3600 N)",
            LineString,
        ),
        ("200-250 E 40TH ST", LineString),  # unable to find addresss
        (
            "N WHIPPLE ST & W BLOOMINGDALE AVE & N HUMBOLDT BLVD W & W CORTLAND ST",
            Polygon,
        ),
        (
            "1400 N CAMPBELL AVE; N CAMPBELL AVE & W LE MOYNE ST & W HIRSCH ST & N MAPLEWOOD AVE",
            Polygon,
        ),
        (
            "6754 S EUCLID AVE; ON W 68TH ST FROM S BENNETT AVE  (1900 E) TO S EUCLID AVE  (1930 E)",
            GeometryCollection,
        ),
        ("1110 N STATE ST; 1030 N STATE ST", MultiPoint),
        # 'ON W EVERGREEN AVE FROM N MILWAUKEE AVE  (1800 W) TO W SCHILLER ST  (1900 W)' # on transportation reported as cross with "Wicher Park AVE",
        # null cases
        ("N MILWAUKEE AVE & N HONORE ST", Point),
        ("W DIVISION ST & N PAULINA ST", Point),
        (
            "ON N HONORE ST FROM N WICKER PARK AVE (1500 N) TO N MILWAUKEE AVE (1520 N)",
            LineString,
        ),
        (
            "ON W DELAWARE PL FROM N DEARBORN ST (40 W) TO N CLARK ST (100 W)",
            LineString,
        ),
        ("S DR MARTIN LUTHER KING JR DR & E 42ND ST", Point),
        ("ON W BARRY AVE FROM N BROADWAY ST (599 W) TO N CLARK ST (800 W)", LineString),
        (
            "ON W BRIAR PL FROM N BROADWAY ST (599 W) TO N HALSTED ST (800 W)",
            LineString,
        ),
        (
            "ON W OAKDALE AVE FROM N CLARK ST (700 W) TO N PINE GROVE AVE (500 W)",
            LineString,
        ),
        (
            "ON W SURF ST FROM N PINE GROVE AVE (510 W) TO N CLARK ST (700 W)",
            LineString,
        ),
        (
            "ON W SURF ST FROM N PINE GROVE AVE (510 W) TO N SHERIDAN RD (400 W)",
            LineString,
        ),
        (
            "ON W WELLINGTON AVE FROM N BROADWAY ST (599 W) TO N CLARK ST (730 W)",
            LineString,
        ),
        (
            "ON W WELLINGTON ST FROM N BROADWAY ST (599 W) TO N CLARK ST (730 W)",
            LineString,
        ),
        ("ON W 125TH PL FROM 50  W TO S STATE ST  (0 E)", LineString),
        ("ON S MANISTEE AVE FROM 10300 S TO E 104TH ST  (10400 S)", LineString),
        ("W 43RD ST &  S HALSTED ST; S LOCK ST &  S LYMAN ST", MultiPoint),
    ],
)
@pytest.mark.integration_test
def test_geocoder_api_process_real_locations(
    test_location: str, expected_result_type: geometry
):
    location_geocoder = LocationGeocoder(geocoder=GeoCoderAPI())
    result = location_geocoder.process_location_text(text=test_location)
    assert type(result) is expected_result_type


@pytest.mark.parametrize(
    "test_location",
    [
        "1400 N WRONG AVE",
        "jkdfhgjkoahfiea",
        "N NOPE AVE & W HGFYHREAS ST & W OFFLIMIT ST & N GHTUEIFGHUS AVE",
    ],
)
@pytest.mark.integration_test
def test_geocoder_api_process_fake_locations(test_location: str):
    location_geocoder = LocationGeocoder(geocoder=GeoCoderAPI())
    result = location_geocoder.process_location_text(text=test_location)
    assert result is None
