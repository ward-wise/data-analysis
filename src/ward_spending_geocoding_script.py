import pandas as pd
import geopandas as gpd
import importlib.metadata

import chicago_participatory_urbanism.ward_spending.address_format_processing as afp
import chicago_participatory_urbanism.ward_spending.address_geocoding as ag

data = gpd.read_file([p for p in importlib.metadata.files('chicago_participatory_urbanism')
                       if '2019-2022 data.csv' in str(p)][0])

data["geometry"] = data["location"].astype(str).apply(ag.process_location_text)
data.to_file('data/output/2019-2022 data_geocoded.geojson', driver='GeoJSON')


