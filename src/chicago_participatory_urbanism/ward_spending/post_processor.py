import pandas as pd

from src.chicago_participatory_urbanism.ward_spending.categorization import (
    get_menu_category,
)


def post_process_data(file_name: str, year: int):
    # load in data and mark year
    data = pd.read_csv(file_name, index_col=None)
    # remove year from items and add as new column
    data["item"] = data["item"].str.replace(r"\s\(\d+\)", "", regex=True)
    data["year"] = year
    # convert cost column to numeric
    data["cost"] = data["cost"].str.replace("[\$,]", "", regex=True).astype(float)

    # add category
    data["category"] = data["item"].apply(get_menu_category)

    # alternative categorization, not implemented
    # map to standard categories
    # data["category"] = data["item"].replace(STANDARD_CATEGORY, regex=True)
    # # remaining categories are "Misc."
    # data['category'] = data['category'].fillna("Misc.")

    return data
