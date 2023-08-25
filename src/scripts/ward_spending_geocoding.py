import pandas as pd
import geopandas as gpd
import importlib.metadata

import chicago_participatory_urbanism.ward_spending.location_format_processing as lfp
import chicago_participatory_urbanism.ward_spending.location_geocoding as lg

data = gpd.read_file([p for p in importlib.metadata.files('chicago_participatory_urbanism')
                       if '2019-2022 data.csv' in str(p)][0])

data["geometry"] = data["location"].astype(str).apply(lg.process_location_text)
data.to_file('data/output/2019-2022 data_geocoded.geojson', driver='GeoJSON')


