# -*- coding: utf-8 -*-

import pandas as pd
from openpyxl import load_workbook
import os
import sys


class CompareFiles:
    """
    Currently compatible only with .txt and .csv files.
    Default separator for csv is ";"
    Default header for csv is 0 (the first line)
    Currently .txt must be WITHOUT header, .csv MUST HAVE header
    """

    def __init__(self, file_1, file_2, header=0, sep=';'):
        self.files_list = [file_1, file_2]
        self.file_1_config = {"name": None, "type": 'csv', "header": header, "sep": sep, "colname": None}
        self.file_2_config = {"name": None, "type": 'csv', "header": header, "sep": sep, "colname": None}
        self.report = {
            "elements": {"file_1": [], "file_2": []},
            "same elements": [],
            "missing elements": {"file_1": [], "file_2": []},
        }

    def update_content(self):
        """
        This creates a list of elements, does not contain the full content
        We compare only certain elements (product codes preferrably), we do not need the full content
        The element can be changed in the "usecol" variable inside self.file_1_config and self.file_2_config
        in csv it will select a column, in txt it will select element in a row of elements
        """
        self.report["elements"]["file_1"] = self.read_file(self.file_1_config)
        self.report["elements"]["file_2"] = self.read_file(self.file_2_config)

    def read_file(self, file_config):
        file_name = file_config["name"]
        file_type = file_config["type"]

        if file_type == "txt":
            elements_list = self.read_txt(file_name, file_config)

        elif file_type == "csv":
            elements_list = self.read_csv(file_name, file_config)

        elif file_type == "xlsx":
            # needs implementation in the future
            pass

        else:
            print("Unsupported file extenstion: {}".format(file_type))
            sys.exit()
        return elements_list

    def read_txt(self, file_name, file_config):
        """
        the rows should look like "data;data;data\n"
        it basically works with txt files that look like csv ones
        that is just because I have some files like that
        """
        elements_list = []
        file = open(file_name)
        content = file.read()
        content = content.split("\n")

        try:
            for row in content:
                row = row.split(file_config["sep"])
                if len(elements_list) == 0:
                    print("1.{}\n2.{}\n3.{}".format(row[0], row[1], row[2]))
                    user_choice = int(input("Which item should I use from the file: {}\n".format(file_name)))
                    user_choice -= 1
                elements_list.append(row[user_choice])
        except IndexError:
            pass

        return elements_list

    def read_csv(self, file_name, file_config):
        elements_list = []
        content = pd.read_csv(
            file_name,
            sep=file_config["sep"],
            header=file_config["header"],
            encoding="latin-1"
        )
        headers_list = [header for header in content]

        for index, header in enumerate(headers_list, start=1):
            print("{}. {}".format(index, header))
        user_choice = int(input("Which column should I use: "))

        user_choice -= 1
        elements_list = [element for element in content[headers_list[user_choice]]]

        return elements_list

    def compare_files(self):
        file_1_elements = self.report["elements"]["file_1"]
        file_2_elements = self.report["elements"]["file_2"]

        self.report["same elements"] = [element for element in file_1_elements if element in file_2_elements]
        self.report["missing elements"]["file_2"] = [element for element in file_1_elements if
                                                     element not in file_2_elements]
        self.report["missing elements"]["file_1"] = [element for element in file_2_elements if
                                                     element not in file_1_elements]

    def print_report(self):
        print("-" * 50)
        print("Number of {} elements: {}".format(self.file_1_config["name"], len(self.report["elements"]["file_1"])))
        print("Number of {} elements: {}".format(self.file_2_config["name"], len(self.report["elements"]["file_2"])))
        print("Number of the same elements: {}".format(len(self.report["same elements"])))
        print("Number of missing elements in the file {}: {}".format(self.file_1_config["name"],
                                                                     len(self.report["missing elements"]["file_1"])))
        print("Number of missing elements in the file {}: {}".format(self.file_2_config["name"],
                                                                     len(self.report["missing elements"]["file_2"])))
        print("-" * 50)

        user_choice = input("Do you want to save the full report to \"report.txt\"? Y/N: ")

        if user_choice == "Y" or user_choice == "y":
            self.save_report()

    def save_report(self):
        with open("report.txt", "w") as file:
            file.write("-" * 50 + "\n")
            file.write(
                "Number of {} elements: {}\n".format(self.file_1_config["name"],
                                                     len(self.report["elements"]["file_1"])))
            file.write(
                "Number of {} elements: {}\n".format(self.file_2_config["name"],
                                                     len(self.report["elements"]["file_2"])))
            file.write("Number of the same elements: {}\n".format(len(self.report["same elements"])))
            file.write("Number of missing elements in the file {}: {}\n".format(self.file_1_config["name"], len(
                self.report["missing elements"]["file_1"])))
            file.write("Number of missing elements in the file {}: {}\n".format(self.file_2_config["name"], len(
                self.report["missing elements"]["file_2"])))
            file.write("-" * 50 + "\n")
            file.write("\n")

            file.write("Missing elements in {}:\n".format(self.file_1_config["name"]))
            for element in self.report["missing elements"]["file_1"]:
                file.write(element + "\n")

            file.write("-" * 50 + "\n")
            file.write("\n")

            file.write("Missing elements in {}:\n".format(self.file_2_config["name"]))
            for element in self.report["missing elements"]["file_2"]:
                file.write(element + "\n")

    def main(self):
        self.update_content()
        self.compare_files()
        self.print_report()


if __name__ == "__main__":
    files = CompareFiles()
    files.main()