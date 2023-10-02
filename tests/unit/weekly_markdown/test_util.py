import unittest
from unittest.mock import mock_open
from unittest import mock
import json

import pandas as pd
from datetime import datetime

from weekly_markdown.util import Util


class TestUtil(unittest.TestCase):
    year = 23
    quarter = "FA"
    start_date = "20230918"
    start_week_number = 1
    total_number_of_weeks = 14
    action = "append"

    config_data = {
        "year": year,
        "quarter": quarter,
        "start_date": start_date,
        "start_week_number": start_week_number,
        "total_number_of_weeks": total_number_of_weeks,
        "action": action,
    }

    @mock.patch("builtins.open", new_callable=mock_open, read_data=json.dumps(config_data))
    def test_init(self, mock_open):
        # Build config content
        config_path = "/mock/path"

        # Assert init setups
        util = Util(config_path)
        self.assertEqual(self.year, util.year)
        self.assertEqual(self.quarter, util.quarter)
        self.assertEqual(datetime.strptime(self.start_date, "%Y%m%d"), util.start_date)
        self.assertEqual(self.start_week_number, util.start_week_number)
        self.assertEqual(self.total_number_of_weeks, util.total_number_of_weeks)
        self.assertEqual(self.action, util.action)

    def test_create_task(self):
        name_tag = Util.create_task("name", "tag")
        no_tag = Util.create_task("name", None)

        self.assertEqual("- [ ] #tag name", name_tag)
        self.assertEqual("- [ ] name", no_tag)

    def test_append_task(self):
        # Build test data content
        test_data = {"Date": "9/29/23", "Name": "mock task", "Tag": "mock-tag", "Frequency": None}
        test_df = pd.DataFrame(test_data)

        find_file_name = ""
        pass
