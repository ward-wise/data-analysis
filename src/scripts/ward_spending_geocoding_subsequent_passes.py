"""Take an existing geojson file and geocode items with missing geometry data."""

import geopandas as gpd

# setup geocoder
from chicago_participatory_urbanism.geocoder_api import GeoCoderAPI
from chicago_participatory_urbanism.ward_spending.location_geocoding import (
    LocationGeocoder,
)

# file paths
input_geojson_file = r"data\2019-2022 data_geocoded.geojson"
output_geojson_file = r"data\output\2019-2022 data_geocoded_new.geojson"


geocoder = GeoCoderAPI()
location_geocoder = LocationGeocoder(geocoder)


# geocode entries with missing geometry data
street_center_lines_gdf = gpd.read_file(input_geojson_file)
for index, row in street_center_lines_gdf.iterrows():
    if row["geometry"] is None:
        location_text = row["location"]
        geometry = location_geocoder.process_location_text(location_text)
        street_center_lines_gdf.at[index, "geometry"] = geometry


street_center_lines_gdf.to_file(output_geojson_file, driver="GeoJSON")
print(f"Updated GeoJSON saved to {output_geojson_file}")
