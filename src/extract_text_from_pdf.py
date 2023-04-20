import PyPDF2
import os
import csv

# Parameters
file_name = '2021 Menu Posting - 22-10-02.pdf'


# Functions

parts = []
def visitor_body(text, cm, tm, fontDict, fontSize):
    y = tm[5]
    if y > 50 and y < 720:
        parts.append(text)

def is_menu_package_item(x):
    return x > 14 and x < 17

def is_location(x):
    return x > 283 and x < 288

def is_cost(x):
    return x > 830 and x < 890

def is_in_table(y):
    return y > 40 and y < 452

def is_ward(x,y):
    return (x > 14 and x < 17) and (y > 490 and y < 510)

def extract_ward_number(text):
    return text.split(':')[-1].strip()

last_y = 0
last_x = 0
ward = 0
def get_table_data(text, cm, tm, fontDict, fontSize):
    global last_x, last_y, ward

    x = tm[4]
    y = tm[5]
    
    if (text != "" and text != "\n"):

        text = text.replace("\n", "")

        if(is_ward(x,y)):
            ward = extract_ward_number(text)
            print("ward: " + ward)
        elif (is_in_table(y)):
            if(is_menu_package_item(x)):
                if (x == last_x and y == last_y):
                    #second line of same item
                    print(text)
                else:
                    print("item: " + text)
            elif(is_location(x)):
                if (x == last_x and y == last_y):
                    # second line of same item
                    print(text)
                else:
                    print("loc: " + text)
            elif(is_cost(x)):
                print("cost: " + text)
            

        last_y = y
        last_x = x


# Main Code

file_path = os.path.join(os.getcwd(), 'data', 'pdf',
                         file_name)
with open(file_path, 'rb') as pdf_file:
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)

    # Loop through each page in the PDF file
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        page.extract_text(visitor_text=get_table_data)


# Write raw text data to a CSV file
output_file_name = file_name[:-4] + '.csv'
output_file_path = os.path.join(os.getcwd(), 'data', 'output',
                         output_file_name)
# with open(output_file_path, "w", newline="") as csvfile:
#     writer = csv.writer(csvfile)

#     lines = extracted_data.split("\n")
#     for line in lines:
#         writer.writerow([line])
