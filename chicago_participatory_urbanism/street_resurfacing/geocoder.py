import pandas as pd
import importlib.metadata
import logging
import geopandas as gpd


# roadway moratorium data from https://data.cityofchicago.org/Transportation/Roadway-Construction-Moratoriums/ndbz-vy4e
# moratorium start dates correspond with when streets were resurfaced
try:
    moratorium_path = [p for p in importlib.metadata.files('chicago_participatory_urbanism')
                        if 'Roadway_Construction_Moratoriums_20231109.csv' in str(p)][0]
    logging.info(f'Loading Moratorium csv data from {moratorium_path.locate()}')
    moratorium_data = pd.read_csv(moratorium_path.locate())
except Exception:
    alternate_path = r'data\street_resurfacing\Roadway_Construction_Moratoriums_20231109.csv'
    logging.warning(f'Moratorium metadata not found. Loading from alternate path: {alternate_path}')
    moratorium_data = pd.read_csv(alternate_path)


# street center lines GeoJSON from https://data.cityofchicago.org/Transportation/Street-Center-Lines/6imu-meau
try:
    street_center_lines_path = [p for p in importlib.metadata.files('chicago_participatory_urbanism')
                        if 'Street Center Lines.geojson' in str(p)][0]
    logging.info(f'Loading street center lines csv from {street_center_lines_path.locate()}')
    gdf = gpd.read_file(street_center_lines_path.locate())
except importlib.metadata.PackageNotFoundError:
    alternate_path = r'data\geocode\Street Center Lines.geojson'
    logging.warning(f'Street centerline metadata not found. Loading from alternate path: {alternate_path}')
    gdf = gpd.read_file(alternate_path)

print("Data loaded.")



# street data has left(l) and right(r) designations for to(t) and from(t) street addresses
# convert to t_add and f_add
gdf['f_add'] = gdf[['r_f_add', 'l_f_add']].min(axis=1)
gdf['t_add'] = gdf[['r_t_add', 'l_t_add']].max(axis=1)
# remove unnecessary fields
gdf = gdf[['pre_dir','street_nam', 'street_typ', 'suf_dir', 'class','f_add','t_add', 'geometry']]
# add new fields
gdf["last_resurf"] = '01/01/1990'
gdf["resurf_count"] = 0
gdf['resurf_dates'] = ""
gdf['m_f_add'] = 0
gdf['m_t_add'] = 0

# filter and sort moratorium data only on street resurfacing
moratorium_data = moratorium_data[(moratorium_data["MORATORIUM TYPE"] =='Street Resurfacing') | (moratorium_data["MORATORIUM TYPE"] =='Planned Street Resurfacing')]
moratorium_data['START DATE timestamp'] = pd.to_datetime(moratorium_data['START DATE'])
moratorium_data = moratorium_data.sort_values(by='START DATE timestamp', ascending=True)

for moratorium_record in moratorium_data:

    street_prefix = moratorium_record['STREET ADDRESS PREFIX']
    street_name = moratorium_record['STREET NAME']
    street_suffix = moratorium_record['STREET NAME SUFFIX']
    start_address = int(moratorium_record['STREET ADDRESS BEGIN'])
    end_address = int(moratorium_record['STREET ADDRESS END'])
    moratorium_type = moratorium_record['MORATORIUM TYPE']
    start_date = moratorium_record['START DATE']

    # filter to street name
    # TODO add suffix to logic
    filtered_gdf = gdf[(gdf['pre_dir'] == street_prefix) | (gdf['street_nam'] == street_name)]

    # filter to street segments
    # check for three cases: start address within segment, end address within segment, segment between start and end address
    filtered_gdf = filtered_gdf[filtered_gdf[
        ((start_address >= gdf['f_add']) & (start_address <= gdf['t_add']) ) | 
        ((end_address >= gdf['f_add']) & (end_address <= gdf['t_add']) ) | 
        ((gdf['f_add'] >= start_address) & (gdf['t_add'] <= end_address) ) 
    ]]

    filtered_gdf["last_resurf"] = start_date
    filtered_gdf["resurf_count"] += 1
    filtered_gdf['resurf_dates'] += start_date + ";"
    filtered_gdf['m_f_add'] = start_address
    filtered_gdf['m_t_add'] = end_address




gdf.to_file(r'data\output\moratium_geocoded.geojson', driver='GeoJSON')


# TODO take partial street segment if address does not go through the whole range
# TODO map classification code (https://data.cityofchicago.org/api/assets/06DEC62C-ACAB-42D3-A540-378F8464F83D?download=true)
# TODO handle multiple resurfacings on same segment
# TODO keep streets that haven't been resurfaced