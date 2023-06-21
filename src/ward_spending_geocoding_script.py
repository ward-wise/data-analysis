import pandas as pd
import geopandas as gpd
import sys
sys.path.append('src')

import chicago_participatory_urbanism.ward_spending.address_format_processing as afp
import chicago_participatory_urbanism.ward_spending.address_geocoding as ag

data = gpd.read_file("data/output/2019-2022 data v1.csv")

data["geometry"] = data["location"].astype(str).apply(ag.process_location_text)
# data.to_csv('C:/Users/seanm/Documents/Python/chicago-participatory-urbanism/data/output/2019-2022 data_geocoded.csv', index=False)
data.to_file('data/output/2019-2022 data_geocoded.geojson', driver='GeoJSON')


