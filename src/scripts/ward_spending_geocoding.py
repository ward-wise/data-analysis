import pandas as pd
import geopandas as gpd
import importlib.metadata
from chicago_participatory_urbanism.ward_spending.location_geocoding import LocationGeocoder

# configure geocoder
from chicago_participatory_urbanism.geocoder import Geocoder
#from chicago_participatory_urbanism.geocoder_api import Geocoder
geocoder = Geocoder()
location_geocoder = LocationGeocoder(geocoder)


data = gpd.read_file([p for p in importlib.metadata.files('chicago_participatory_urbanism')
                       if '2019-2022 data.csv' in str(p)][0])

data["geometry"] = data["location"].astype(str).apply(location_geocoder.process_location_text)
data.to_file('data/output/2019-2022 data_geocoded.geojson', driver='GeoJSON')


