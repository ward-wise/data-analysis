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

logging.info("Data loaded.")



def nonzero_min_f_add(row):
    # some streets have no addresses on one side, which is a 0 from-address in the data
    if row['r_f_add'] == 0:
        return row['l_f_add']
    elif row['l_f_add'] == 0:
        return row['r_f_add']
    else:
        return min(row['r_f_add'], row['l_f_add'])

# column conversions
gdf['l_t_add'] = gdf['l_t_add'].astype(int)
gdf['r_t_add'] = gdf['r_t_add'].astype(int)
gdf['l_f_add'] = gdf['l_f_add'].astype(int)
gdf['r_f_add'] = gdf['r_f_add'].astype(int)
# street data has left(l) and right(r) designations for to(t) and from(t) street addresses
# convert to t_add and f_add
gdf['f_add'] = gdf.apply(nonzero_min_f_add, axis=1).astype(int)
gdf['t_add'] = gdf[['r_t_add', 'l_t_add']].max(axis=1).astype(int)
# remove unnecessary fields
gdf = gdf[['pre_dir','street_nam', 'street_typ', 'suf_dir', 'class','f_add','t_add', 'geometry']]
# drop unnamed streets
gdf = gdf.dropna(subset=['street_nam'])
# add new fields
gdf["last_resurf"] = 0
gdf["resurf_count"] = 0
gdf['resurf_dates'] = ""
gdf['m_f_add'] = 0
gdf['m_t_add'] = 0

# filter and sort moratorium data only on street resurfacing
moratorium_data = moratorium_data[(moratorium_data["MORATORIUM TYPE"] =='Street Resurfacing') | (moratorium_data["MORATORIUM TYPE"] =='Planned Street Resurfacing')]
moratorium_data['START DATE timestamp'] = pd.to_datetime(moratorium_data['START DATE'])
moratorium_data = moratorium_data.sort_values(by='START DATE timestamp', ascending=True)


logging.info("Geocoding road moratorium data...")
for index, moratorium_record in moratorium_data.iterrows():
    street_prefix = moratorium_record['STREET ADDRESS PREFIX']
    street_name = moratorium_record['STREET NAME']
    street_suffix = moratorium_record['STREET NAME SUFFIX']
    start_address = int(moratorium_record['STREET ADDRESS BEGIN'])
    end_address = int(moratorium_record['STREET ADDRESS END'])
    moratorium_type = moratorium_record['MORATORIUM TYPE']
    start_date = moratorium_record['START DATE']
    year = int(start_date.split("/")[-1])

    logging.debug(f"{start_address}-{end_address} {street_prefix} {street_name} {street_suffix}, {year}")

    mask_street = ((gdf['pre_dir'] == street_prefix) & 
                       (gdf['street_nam'] == street_name) &
                       (gdf["street_typ"] == street_suffix))

    # check for three cases: start address within segment, end address within segment, segment between start and end address
    mask_segment = mask_street & (  
        ((start_address >= gdf['f_add']) & (start_address < gdf['t_add']) ) | 
        ((end_address > gdf['f_add']) & (end_address <= gdf['t_add']) ) | 
        ((gdf['f_add'] >= start_address) & (gdf['t_add'] <= end_address) )
    )

    # update data on street segments
    gdf.loc[mask_segment, "last_resurf"] = year
    gdf.loc[mask_segment, "resurf_count"] += 1
    gdf.loc[mask_segment, 'resurf_dates'] += start_date + ";"
    gdf.loc[mask_segment, 'm_f_add'] = start_address
    gdf.loc[mask_segment, 'm_t_add'] = end_address

logging.info("Exporting data...")
gdf.to_file(r'data\output\moratiums_20231109_geocoded.geojson', driver='GeoJSON')


# TODO take partial street segment if address does not go through the whole range
# TODO map classification code (https://data.cityofchicago.org/api/assets/06DEC62C-ACAB-42D3-A540-378F8464F83D?download=true)
