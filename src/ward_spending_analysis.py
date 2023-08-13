import pandas as pd
import re


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


# load data in from different years and mark year
data_2019 = pd.read_csv('explorer/data/menu-postings/2019.csv', index_col=None)
data_2019['year'] = 2019
data_2020 = pd.read_csv('explorer/data/menu-postings/2020.csv', index_col=None)
data_2020['year'] = 2020
data_2021 = pd.read_csv('explorer/data/menu-postings/2021.csv', index_col=None)
data_2021['year'] = 2021
data_2022 = pd.read_csv('explorer/data/menu-postings/2021.csv', index_col=None)
data_2022['year'] = 2022

# combine into one dataset
data = pd.concat([data_2019, data_2020, data_2021, data_2022])
data.reset_index()

## clean up data
# remove year from items and add as new column
data['item'] = data['item'].str.replace(r'\s\(\d+\)', '', regex=True)
# covnert texts to lower case
data['item'] = data['item'].str.lower()
# convert cost column to numeric
data['cost'] = data['cost'].str.replace('[\$,]', '', regex=True).astype(float)
# add category
#data["category"] = data["item"].apply(get_menu_category)

# map to standard categories
data["category"] = data["item"].map(STANDARD_CATEGORY)
# remaining categories are "Misc."
data['category'] = data['category'].fillna("Misc.")
#data.to_csv('data/output/2019-2022 data v1.csv', index=False)

print(data.sample(10))

# potential APIs
# https://nominatim.openstreetmap.org/ui/search.html
# https://wiki.openstreetmap.org/wiki/OSMPythonTools


'''
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

'''