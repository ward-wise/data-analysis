import PyPDF2
import os
import csv

file_name = '2021 Menu Posting - 22-10-02.pdf'
file_path = os.path.join(os.getcwd(), 'data', 'pdf',
                         file_name)


pdf_file = open(file_path, 'rb')
pdf_reader = PyPDF2.PdfReader(pdf_file)
num_pages = len(pdf_reader.pages)


text_data = []
# Loop through each page in the PDF file
for page_num in range(num_pages):
    page = pdf_reader.pages[page_num]
    text_data.append(page.extract_text())

pdf_file.close()


# Write raw text data to a CSV file
output_file_name = file_name[:-4] + '.csv'
output_file_path = os.path.join(os.getcwd(), 'data', 'output',
                         output_file_name)
with open(output_file_path, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    for page in text_data:
        lines = page.split("\n")
        for line in lines:
            writer.writerow([line])
