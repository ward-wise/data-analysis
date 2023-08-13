import PyPDF2
import os
import csv
import re

# Parameters
file_name = '2020 Menu Posting - 22-10-02.pdf'
#file_name = '2022 Menu - 2-9-23.pdf'

# below numbers work for 2019+ format of menu posting PDFs

# Functions

def is_menu_package_item(x):
    return x > 14 and x < 17

def is_location(x):
    return x > 283 and x < 288

def is_cost(x):
    return x > 830 and x < 890

def is_in_table(y):
    return y > 30 and y < 460

def is_ward(x,y):
    return (x > 14 and x < 17) and (y > 490 and y < 510)

def extract_ward_number(text):
    return text.split(':')[-1].strip()

last_y = 0
last_x = 0
ward = 0
data = []
current_row = {"ward": 0, "item": "", "loc": "", "cost": ""}
def get_table_data(text, cm, tm, fontDict, fontSize):
    global last_x, last_y, ward, data, current_row

    x = tm[4]
    y = tm[5]

    if (text != "" and text != "\n"):

        text = text.replace("\n", "").strip()

        if(is_ward(x,y)):
            ward = extract_ward_number(text)
            print("ward: " + ward)
        elif (is_in_table(y)):

            y_diff = last_y - y
            if(y_diff> 15 or y_diff<-50):
                # new item!
                data.append(current_row)
                current_row = {"ward": ward, "item": "", "loc": "", "cost":""}

            if(is_menu_package_item(x)):
                item_text = text
                if (x == last_x and y == last_y):
                    # second line of same item, need to add a space
                    item_text = " " + item_text

                current_row["item"] += item_text

            elif(is_location(x)):
                loc_text = text
                if (x == last_x and y == last_y):
                    # second line of same loc, need to add a space
                    loc_text = " " + loc_text

                current_row["loc"] += loc_text

            elif(is_cost(x)):
                current_row["cost"] += text


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

        # reset last_x and last_y for new page
        # needed to prevent issue when item on next page matches coords of last item on previous page
        last_y = 0
        last_x = 0

        page = pdf_reader.pages[page_num]
        page.extract_text(visitor_text=get_table_data)


# Write raw text data to a CSV file
output_file_name = file_name[:-4] + '.csv'
output_file_path = os.path.join(os.getcwd(), 'data', 'output',
                         output_file_name)
with open(output_file_path, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    # headers
    writer.writerow(["ward","item", "location", "cost"])

    for row in data:
        if ((row["item"] != "MENU BUDGET")
            and not (re.search("WARD COMMITTED 20\d\d TOTAL", row["item"]))
            and not (re.search("WARD 20\d\d BALANCE", row["item"]))
            and row["ward"] != 0):
            writer.writerow(row.values())
