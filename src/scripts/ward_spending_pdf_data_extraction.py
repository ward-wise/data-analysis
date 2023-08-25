import os
from chicago_participatory_urbanism.ward_spending.extract_text_from_pdf import extract_pdf_data

pdf_file_name = '2020 Menu Posting - 22-10-02.pdf'
output_file_name = pdf_file_name[:-4] + '.csv'

pdf_file_path = os.path.join(os.getcwd(), 'data', 'pdf', pdf_file_name)
output_file_path = os.path.join(os.getcwd(), 'data', 'output', output_file_name)


extract_pdf_data(pdf_file_path, output_file_path)