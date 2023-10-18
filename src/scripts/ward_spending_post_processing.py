import pandas as pd
from chicago_participatory_urbanism.ward_spending.post_processor import post_process_data
import re
import os

files = ['2019 Menu Posting - 22-10-02.csv', 
         '2020 Menu Posting - 22-10-02.csv',
         '2021 Menu Posting - 22-10-02.csv',
         '2022 Menu - 2-9-23.csv']

year_pattern = r"20\d{2}"
dataframes = []
for file in files:
    match = re.search(year_pattern, file)
    if match:
        year = match.group()
    else:
        year = 0
    print(f"Processing {year} data...")
    file_path = os.path.join(os.getcwd(), 'data', 'output', file)
    dataframes.append(post_process_data(file_path, year))

# combine into one dataset
print(f"Joining data...")
data = pd.concat(dataframes)
data.reset_index()

# export data
output_file_path = 'data/output/2019-2022 data.csv'
data.to_csv(output_file_path, index=False)
print(f"Post-processing complete. Data saved to {output_file_path}.")