import csv
import re

import PyPDF2

# below numbers work for 2019+ format of menu posting PDFs


# Functions
def _is_menu_package_item(x):
    return x > 14 and x < 17


def _is_location(x):
    return x > 283 and x < 288


def _is_cost(x):
    return x > 830 and x < 890


def _is_in_table(y):
    return y > 30 and y < 460


def _is_ward(x, y):
    return (x > 14 and x < 17) and (y > 490 and y < 510)


def _extract_ward_number(text):
    return text.split(":")[-1].strip()


class WardSpendingPDFTextExtractor:
    def __init__(self, pdf_file_path: str, output_file_path: str):
        self.pdf_file_path = pdf_file_path
        self.output_file_path = output_file_path

        self.last_y = 0
        self.last_x = 0
        self.ward = 0
        self.data = []
        self.current_row = {"ward": 0, "item": "", "loc": "", "cost": ""}

    def _get_table_data(self, input_text, _cm, tm, _fontDict, _fontSize):
        x = tm[4]
        y = tm[5]

        if input_text not in ("", "\n"):
            input_text = input_text.replace("\n", "").strip()

            if _is_ward(x, y):
                self.ward = _extract_ward_number(input_text)

            elif _is_in_table(y):
                y_diff = self.last_y - y
                if y_diff > 15 or y_diff < -50:
                    # new item!
                    self.data.append(self.current_row)
                    self.current_row = {"ward": self.ward, "item": "", "loc": "", "cost": ""}

                if _is_menu_package_item(x):
                    item_text = input_text
                    if x == self.last_x and y == self.last_y:
                        # second line of same item, need to add a space
                        item_text = " " + item_text

                    self.current_row["item"] += item_text

                elif _is_location(x):
                    loc_text = input_text
                    if x == self.last_x and y == self.last_y:
                        # second line of same loc, need to add a space
                        loc_text = " " + loc_text

                    self.current_row["loc"] += loc_text

                elif _is_cost(x):
                    self.current_row["cost"] += input_text

                self.last_y = y
                self.last_x = x

    # Main function

    def extract_pdf_data(self):
        with open(self.pdf_file_path, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)

            # Loop through each page in the PDF file
            for page_num in range(num_pages):
                # reset last_x and last_y for new page
                # needed to prevent issue when item on next page matches coords of last item on previous page
                self.last_y = 0
                self.last_x = 0

                page = pdf_reader.pages[page_num]
                page.extract_text(visitor_text=self._get_table_data)

        # Write raw text data to a CSV file
        with open(self.output_file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)

            # headers
            writer.writerow(["ward", "item", "location", "cost"])

            for row in self.data:
                if (
                    (row["item"] != "MENU BUDGET")
                    and not (re.search("WARD COMMITTED 20\d\d TOTAL", row["item"]))
                    and not (re.search("WARD 20\d\d BALANCE", row["item"]))
                    and row["ward"] != 0
                ):
                    writer.writerow(row.values())
