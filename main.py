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

weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

filename = "./config.yaml"

with open(filename, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
    print(config)

year = config["year"]
quarter = config["quarter"]
save_path = config["save_path"]


# Convert string to datetime object
start_date = datetime.strptime(config["start_date"], date_format)

start_week_number = int(config["start_week_number"])
total_number_of_weeks = int(config["total_number_of_weeks"])

final_week = int(start_week_number+total_number_of_weeks)

while final_week != start_week_number:

    name = f"{year}-{quarter}-{start_week_number:02} ({start_date.strftime('%m-%d')})"
    mdFile = MdUtils(file_name=os.path.join(save_path, name))

    n = 0

    while n != 7:
        
        # Format the datetime object to string with month and day
        formatted_date = start_date.strftime("%m-%d")

        mdFile.new_header(level=1, title=f"{weekdays[n]} {formatted_date}")
       
        # Add one day
        start_date = start_date + timedelta(days=1)
        n += 1

    mdFile.create_md_file()

    # Exit loop by updating variable
    start_week_number += 1
