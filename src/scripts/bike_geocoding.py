import os

import geopandas as gpd
from shapely.geometry import LineString

from src import chicago_participatory_urbanism as geocoder


def process_street_segment(primary_street, cross_street1, cross_street2):
    try:
        point1 = geocoder.get_intersection_coordinates(primary_street, cross_street1)
        point2 = geocoder.get_intersection_coordinates(primary_street, cross_street2)
        street_segment = LineString([point1, point2])
        return street_segment
    except Exception:
        return None


def generate_bikeway_installations_geocoding():
    data = gpd.read_file(os.path.join(os.getcwd(), "data", "CDOT Bikeway Installations.csv"))

    data["geometry"] = data.apply(
        lambda row: process_street_segment(row["Street"], row["From"], row["To"]),
        axis=1,
    )
    data.to_file(
        os.path.join(os.getcwd(), "data", "CDOT Bikeway Installations.geojson"),
        driver="GeoJSON",
    )
