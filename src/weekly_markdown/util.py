#!/usr/bin/env python3
import os
from pathlib import Path
import warnings
import yaml

from mdutils.mdutils import MdUtils
from mdutils import Html

from datetime import datetime, timedelta
date_format = "%Y%m%d"

warnings.simplefilter("ignore")

class Util():
    # Define global variables
    def __init__(self) -> None:
        self.weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.config = self.open_file("./src/config.yaml")
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
        self.start_date = datetime.strptime(self.config["start_date"], date_format)

        self.start_week_number = int(self.config["start_week_number"])
        self.total_number_of_weeks = int(self.config["total_number_of_weeks"])
    
    def find_files(self, path, suffix=False):
        accumulated_files = []

        final_week = int(self.start_week_number+self.total_number_of_weeks)
        start = self.start_week_number
        start_date = self.start_date

        while final_week != start:

            name = f"{self.year}-{self.quarter}-{start:02} ({start_date.strftime('%m-%d')})"
            if suffix:
                name = name + ".md"
            accumulated_files.append(os.path.join(path, name))

            start_date = start_date + timedelta(days=7)
            
            # Exit loop by updating variable
            start += 1
        return accumulated_files


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
    
    def append_tasks(self, task_path) -> None:
        """
        Append tasks under the corresponding date.
        """
        config = self.open_file("./configs/append.yaml")
        path = config['append_path']

        print("This function is not implemented yet. Thank you for your patience!")
        