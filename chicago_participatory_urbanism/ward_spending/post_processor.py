import pandas as pd
# from categorization import STANDARD_CATEGORY
# from location_geocoding import LocationGeocoder
# from geocoder_api import GeoCoderAPI
import multiprocessing as mp


STANDARD_CATEGORY = {
    "pedestrian": "Pedestrian Infrastructure",
    "bump outs": "Pedestrian Infrastructure",
    "bicycle": "Bicycle Infrastructure",
    "bike": "Bicycle Infrastructure",
    "neighborhood greenway": "Bicycle Infrastructure",
    "light": "Lighting",
    "street resurfacing": "Street Resurfacing",
    "street speed hump replacement": "Street Resurfacing",
    "curb & gutter": "Street Resurfacing",
    "alley": "Alleys",
    "miscellaneous cdot projects": "Misc. CDOT",
    "mural": "Beautification",
    "public art": "Beautification",
    "tree planting": "Beautification",
    "turn arrow": "Street Redesign",
    "street speed hump menu": "Street Redesign",
    "pavement markings": "Street Redesign",
    "traffic circle": "Street Redesign",
    "cul-de-sac": "Street Redesign",
    "diagnol parking": "Street Redesign",
    "sidewalk": "Sidewalk Repair",
    "pod camera": "Police Cameras",
    "park": "Parks",
    "playground": "Parks",
    "garden": "Parks",
    "viaduct": "Viaducts",
}

def post_process_data(file_name: str, year: int):
    # load in data and mark year
    data = pd.read_csv(file_name, index_col=None)
    # remove year from items and add as new column
    data['item'] = data['item'].str.replace(r'\s\(\d+\)', '', regex=True)
    data['year'] = year
    # convert cost column to numeric
    data['cost'] = data['cost'].str.replace('[\$,]', '', regex=True).astype(float)
    
    # add category
    #data["category"] = data["item"].apply(get_menu_category)

    # map to standard categories
    data["category"] = data["item"].replace(STANDARD_CATEGORY, regex=True)
    # remaining categories are "Misc."
    data['category'] = data['category'].fillna("Misc.")

    return data


if __name__ == '__main__':
    import time
    start = time.time()
    data = post_process_data(file_name='data/ward_spending/2019-2022 data.csv')
    geo_coder_method = GeoCoderAPI()
    geo_coder = LocationGeocoder(geocoder=geo_coder_method)
    with mp.Pool(mp.cpu_count()) as pool:
        data_geo_code = pool.map(geo_coder.process_location_text, data[:100]['location'])
    # for row in data[:100].itertuples():
    #     geo_coder.process_location_text(text=row[3])

    end = time.time()
    print(data_geo_code)
    print(f'{end-start} seconds')
