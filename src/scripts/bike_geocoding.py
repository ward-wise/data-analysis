import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import importlib.metadata

import chicago_participatory_urbanism.geocoder as geocoder

def process_street_segment(primary_street, cross_street1, cross_street2):
    try:
        point1 = geocoder.get_intersection_coordinates(primary_street, cross_street1)
        point2 = geocoder.get_intersection_coordinates(primary_street, cross_street2)
        street_segment = LineString([point1, point2])
        return street_segment
    except Exception:
        return None

data = gpd.read_file([p for p in importlib.metadata.files('chicago_participatory_urbanism')
                          if 'CDOT Bikeway Installations.csv' in str(p)][0])


data["geometry"] = data.apply(lambda row: process_street_segment(row['Street'], row['From'], row['To']), axis=1)
data.to_file('data/output/CDOT Bikeway Installations.geojson', driver='GeoJSON')





