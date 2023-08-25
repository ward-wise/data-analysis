import pandas as pd
from ward_spending.categorization import STANDARD_CATEGORY

def post_process_data(file_name: str, year: int):
    # load in data and mark year
    data = pd.read_csv(file_name, index_col=None)
    data['year'] = year

    ## clean up data
    # remove year from items and add as new column
    data['item'] = data['item'].str.replace(r'\s\(\d+\)', '', regex=True)
    # convert texts to lower case
    data['item'] = data['item'].str.lower()
    # convert cost column to numeric
    data['cost'] = data['cost'].str.replace('[\$,]', '', regex=True).astype(float)
    # add category
    #data["category"] = data["item"].apply(get_menu_category)

    # map to standard categories
    data["category"] = data["item"].map(STANDARD_CATEGORY)
    # remaining categories are "Misc."
    data['category'] = data['category'].fillna("Misc.")

    return data