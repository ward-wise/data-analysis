import os

import geopandas as gpd

from src.chicago_participatory_urbanism.ward_spending.location_geocoding import (
    LocationGeocoder,
)


def generate_ward_spending_geocoding():
    # use local geocoder
    # from chicago_participatory_urbanism.geocoder import Geocoder
    # geocoder = Geocoder()

    # use geocoder APIs
    from src.chicago_participatory_urbanism.geocoder_api import GeoCoderAPI

    geocoder = GeoCoderAPI()

    location_geocoder = LocationGeocoder(geocoder)

    file_path = os.path.join(os.getcwd(), "data", "output", "2019-2022 data.csv")
    data = gpd.read_file(file_path)

    data["geometry"] = data["location"].astype(str).apply(location_geocoder.process_location_text)
    data.to_file(file_path[:-4] + "_geocoded.geojson", driver="GeoJSON")
