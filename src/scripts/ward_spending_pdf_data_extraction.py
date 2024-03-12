import os
from src.chicago_participatory_urbanism.ward_spending.extract_text_from_pdf import (
    extract_pdf_data,
)

# Download these files to the data/pdf folder from the Chicago Capital Improvement Archive
files = [
    "2019 Menu Posting - 22-10-02.pdf",
    "2020 Menu Posting - 22-10-02.pdf",
    "2021 Menu Posting - 22-10-02.pdf",
    "2022 Menu - 2-9-23.pdf",
]


def extract_from_files():
    for pdf_file_name in files:
        output_file_name = pdf_file_name[:-4] + ".csv"

        print(f'Extracting data from "{pdf_file_name}"...')
        pdf_file_path = os.path.join(os.getcwd(), "data", "pdf", pdf_file_name)
        output_file_path = os.path.join(os.getcwd(), "data", "output", output_file_name)
        print(f'Data saved to "{output_file_path}".')

        extract_pdf_data(pdf_file_path, output_file_path)
