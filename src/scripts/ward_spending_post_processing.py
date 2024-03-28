import logging
import os
import re

import pandas as pd

from src.chicago_participatory_urbanism.ward_spending.post_processor import (
    post_process_data,
)

files = [
    "2019 Menu Posting - 22-10-02.csv",
    "2020 Menu Posting - 22-10-02.csv",
    "2021 Menu Posting - 22-10-02.csv",
    "2022 Menu - 2-9-23.csv",
]


def postprocess_and_combine_data():
    year_pattern = r"20\d{2}"
    dataframes = []
    for file in files:
        match = re.search(year_pattern, file)
        year = match.group() if match else 0
        logging.info(f"Processing {year} data...")
        file_path = os.path.join("data", "output", file)
        dataframes.append(post_process_data(file_path, year))

    # combine into one dataset
    logging.info("Joining data...")
    data = pd.concat(dataframes)
    data.reset_index()

    # export data
    output_file_path = "data/output/2019-2022 data.csv"
    data.to_csv(output_file_path, index=False)
    logging.info(f"Post-processing complete. Data saved to {output_file_path}.")
