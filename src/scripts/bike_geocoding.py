import geopandas as gpd
import os
from shapely.geometry import LineString
from src.chicago_participatory_urbanism.location_structures import Intersection, Street
from src.chicago_participatory_urbanism.geocoder_api import GeoCoderAPI
geocoder = GeoCoderAPI()

def process_street_segment(primary_street_name, cross_street1_name, cross_street2_name):
    try:
        primary_street = Street(direction="", name=primary_street_name, street_type="")
        cross_street1 = Street(direction="", name=cross_street1_name, street_type="")
        cross_street2 = Street(direction="", name=cross_street2_name, street_type="")
    
        point1 = geocoder.get_intersection_coordinates(Intersection(primary_street, cross_street1))
        point2 = geocoder.get_intersection_coordinates(Intersection(primary_street, cross_street2))
        street_segment = LineString([point1, point2])
        return street_segment
    except Exception as e:
        print(e)
        return None


def generate_bikeway_installations_geocoding():

    data = gpd.read_file(os.path.join(os.getcwd(), 'data', 'CDOT Bikeway Installations.csv'))
    data["geometry"] = data.apply(lambda row: process_street_segment(row['Street'], row['From'], row['To']), axis=1)
    data.to_file(os.path.join(os.getcwd(), 'data', 'CDOT Bikeway Installations.geojson'), driver='GeoJSON')
