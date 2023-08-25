import pandas as pd
from chicago_participatory_urbanism.ward_spending.post_processor import post_process_data
import re

files = ['data/output/2019.csv', 
         'data/output/2020.csv',
         'data/output/2021.csv', 
         'data/output/2021.csv']

year_pattern = r"20\d{2}$"
dataframes = []
for file in files:
    match = re.search(year_pattern, file)
    if match:
        year = match.group()
    else:
        year = 0
    dataframes.append(post_process_data(file, year))

# combine into one dataset
data = pd.concat(dataframes)
data.reset_index()

# export data
data.to_csv('data/output/2019-2022.csv', index=False)