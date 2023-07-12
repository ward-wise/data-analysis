import geopandas as gpd
import pandas as pd
import re

def get_menu_category(item):
    item = item.lower()
    if ("pedestrian" in item 
        or "bump outs" in item):
        return "Pedestrian Infrastructure"
    elif ("bicycle" in item
          or "bike" in item
          or "neighborhood greenway" in item):
        return "Bicycle Infrastructure"
    elif "light" in item:
        return "Lighting"
    elif("street resurfacing" in item 
         or "street speed hump replacement" in item 
         or "curb & gutter" in item):
        return "Street Resurfacing"
    elif "alley" in item:
        return "Alleys"
    elif "miscellaneous cdot projects" in item:
        return "Misc. CDOT"
    elif ("mural" in item
          or "public art" in item
          or "tree planting" in item):
        return "Beautification"
    elif ("turn arrow" in item 
          or "street speed hump menu" in item 
          or "pavement markings" in item 
          or "traffic circle" in item 
          or "cul-de-sac" in item
          or "diagnol parking" in item):
        return "Street Redesign"
    elif "sidewalk" in item:
        return "Sidewalk Repair"
    elif "pod camera" in item:
        return "Police Cameras"
    elif ("park" in item
          or "playground" in item
          or "garden" in item):
        return "Parks"
    elif ("viaduct" in item):
        return "Viaducts"
    else:
        return "Misc."
    

# load data in from different years and mark year
data_2019 = gpd.read_file("data/output/2019 Menu Posting - 22-10-02.csv")
data_2019['year'] = 2019
data_2020 = gpd.read_file("data/output/2020 Menu Posting - 22-10-02.csv")
data_2020['year'] = 2020
data_2021 = gpd.read_file("data/output/2021 Menu Posting - 22-10-02.csv")
data_2021['year'] = 2021
data_2022 = gpd.read_file("data/output/2022 Menu - 2-9-23.csv")
data_2022['year'] = 2022

# combine into one dataset
data = pd.concat([data_2019, data_2020, data_2021, data_2022])

## clean up data
# remove year from items and add as new column
data['item'] = data['item'].str.replace(r'\s\(\d+\)', '', regex=True)
# convert cost column to numeric
data['cost'] = data['cost'].str.replace('[\$,]', '', regex=True).astype(float)
# add category
data["category"] = data["item"].apply(get_menu_category)

data.to_csv('data/output/2019-2022 data v1.csv', index=False)
