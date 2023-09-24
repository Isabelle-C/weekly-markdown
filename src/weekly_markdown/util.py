#!/usr/bin/env python3
import os
from pathlib import Path
import warnings
import yaml
import re

from mdutils.mdutils import MdUtils
from mdutils import Html
import math
import pandas as pd

from datetime import datetime, timedelta

warnings.simplefilter("ignore")


class Util:
    # Define global variables
    def __init__(self, config_path) -> None:
        self.weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.config = self.open_file(config_path)
        self.action = self.config["action"]
        self.set_additional_attributes()

    @staticmethod
    def open_file(path):
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return config

    def set_additional_attributes(self):
        self.year = self.config["year"]
        self.quarter = self.config["quarter"]

        # Convert string to datetime object
        self.start_date = datetime.strptime(self.config["start_date"], "%Y%m%d")

        self.start_week_number = int(self.config["start_week_number"])
        self.total_number_of_weeks = int(self.config["total_number_of_weeks"])

        self.final_day = self.start_date + timedelta(days=7 * (self.total_number_of_weeks))

    def find_files(self, path, suffix=False) -> list:
        """
        Find all the file paths with specified parameters.

        Parameters
        ----------
        path : str
            Path to files.
        suffix : bool
            True if file names need suffix, False otherwise.

        Return
        ------
        : list
            List of file paths.
        """
        accumulated_files = []

        final_week = int(self.start_week_number + self.total_number_of_weeks)
        current_week = self.start_week_number
        start_date = self.start_date

        while final_week != current_week:
            name = f"{self.year}-{self.quarter}-{current_week:02} ({start_date.strftime('%m-%d')})"
            if suffix:
                name = name + ".md"
            accumulated_files.append(os.path.join(path, name))

            start_date = start_date + timedelta(days=7)

            # Exit loop by updating variable
            current_week += 1
        return accumulated_files

    def add_recurring_task(self, date, name, tag, path):
        """
        Add recurring tasks.

        Parameters
        ----------
        date : datetime
            Date of the task.
        name : str
            Name of the task.
        tag : str
            Tag of the task.
        """
        task_date = date

        while task_date != self.final_day:
            self.add_one_task(task_date, name, tag, path)
            current_month = task_date.month
            task_date = task_date.replace(month=current_month + 1)

    @staticmethod
    def create_task(name, tag) -> str:
        """
        Create task to be appended to markdown file.
        """
        if not math.isnan(tag):
            if " " in tag:
                raise ValueError("Tag must not contain space")
            elif tag.isnumeric():
                raise ValueError("Tag must not be all numbers")
            else:
                add_task = f"- [ ] #{tag} {name}"
        else:
            add_task = f"- [ ] {name}"
        return add_task

    def add_one_task(self, date, name, tag, path):
        """
        Find the file for appending data and and task.
        """

        all_files = self.find_files(path, True)

        # subtract date from original date
        datediff = (date - self.start_date).days
        print(datediff)
        # result/7 - 1 = index from find all files
        if datediff < 0:
            raise ValueError("Date is before the start date")
        elif datediff == 0:
            file_index = 0
        else:
            file_index = datediff // 7
            print(file_index)

        file = all_files[file_index]
        # append task to file
        with open(file, "r") as f:
            pattern = rf"{date.month:02}-{date.day:02}"
            original_content = f.read()
            new_content = Util.create_task(name, tag)
            
            if re.search(pattern, original_content) is None:
                raise ValueError("Date is not found in the file")
            else:
                modified_content = re.sub(pattern, rf"{date.month:02}-{date.day:02}\0\n" + new_content, original_content)
                with open(file, "w") as f:
                    f.write(modified_content)

    def run(self):
        if self.action == "create":
            self.create_data()
        elif self.action == "archive":
            self.move_files()
        elif self.action == "append":
            self.append_tasks()
        else:
            raise ValueError("Invalid action was provided")

    def create_data(self):
        """
        Add dates to markdown files.
        """
        config = self.open_file("./configs/create.yaml")
        path = config["save_path"]

        accumulated_files = self.find_files(path)
        start_date = self.start_date

        for f in accumulated_files:
            mdFile = MdUtils(file_name=f)

            n = 0

            while n != 7:
                # Format the datetime object to string with month and day
                formatted_date = start_date.strftime("%m-%d")

                mdFile.new_header(level=1, title=f"{self.weekdays[n]} {formatted_date}")

                # Add one day
                start_date = start_date + timedelta(days=1)
                n += 1

            mdFile.create_md_file()

    def move_files(self) -> None:
        """
        Move files from one directory to another.
        """
        config = self.open_file("./configs/archive.yaml")
        original_path = config["original_path"]
        new_path = config["new_path"]

        accumulated_files = self.find_files(original_path, True)
        new_accumulated_files = self.find_files(new_path, True)
        for f, new_f in zip(accumulated_files, new_accumulated_files):
            if os.path.exists(f):
                os.rename(f, new_f)

    def append_tasks(self) -> None:
        """
        Append tasks under the corresponding date.
        """
        config = self.open_file("./configs/append.yaml")

        path = config["append_path"]
        task_path = config["task_path"]

        # check the end of the path
        if Path(task_path).suffix == ".csv":
            tasks = pd.read_csv(task_path)
        elif Path(task_path).suffix == ".xlsx":
            tasks = pd.read_excel(task_path)
        else:
            raise ValueError("Provide either csv or excel file")

        # iterate over pandas dataframe

        for _, row in tasks.iterrows():
            date = row["Date"]
            name = row["Name"]
            tag = row["Tag"]
            freq = row["Frequency"]
            
            if isinstance(freq, str):
                self.add_recurring_task(date, name, tag, path)
            elif math.isnan(freq):
                self.add_one_task(date, name, tag, path)
            else:
                raise ValueError("Frequency must be either NaN or string")