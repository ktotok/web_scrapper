import json
import argparse
import re
from datetime import datetime

import requests
from requests import codes
from bs4 import BeautifulSoup, Tag

parser = argparse.ArgumentParser(description='Process url with x12 codes.')

parser.add_argument('url', type=str, help='target url to process')
parser.add_argument('-started', type=str,
                    help='Retrieve code items started since specified date. Format: \'mm/dd/YYY\'')
parser.add_argument('-modified', type=str, help='Retrieve code items modified at specified date. Format: \'mm/dd/YYY\'')
args = parser.parse_args()

target_url = args.url
started_date = datetime.strptime(args.started, "%m/%d/%Y") if args.started is not None else None
modified_date = datetime.strptime(args.modified, "%m/%d/%Y") if args.modified is not None else None

req = requests.get(target_url)
assert req.status_code == codes.OK

html_content = req.text

soup = BeautifulSoup(html_content, 'html.parser')

x12_codes_dict = []
for row_tag in soup.select(".prod_set.current"):

    row_dates = row_tag.select_one(".description .dates").text
    assert row_dates
    row_dates = re.findall("(\d{2}\/\d{2}\/\d{4})", row_dates)

    if started_date is not None:
        row_started_date = datetime.strptime(row_dates[0], "%m/%d/%Y")

        if row_started_date < started_date:
            continue

    if modified_date is not None:
        if len(row_dates) < 2:
            continue

        row_modified_date = datetime.strptime(row_dates[1], "%m/%d/%Y")

        if row_modified_date < modified_date:
            continue

    code_value = row_tag.select_one(".code").text
    description_value = row_tag.select_one(".description").contents[0] \
        if not isinstance(row_tag.select_one(".description").contents[0], Tag) \
        else row_tag.select_one(".description").contents[1]

    x12_codes_dict.append(
        {
            "code": code_value,
            "description": description_value
        })

x12_codes_json = json.dumps(x12_codes_dict, indent='\t')
print(x12_codes_json)
