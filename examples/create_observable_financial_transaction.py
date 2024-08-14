# coding: utf-8
from dateutil.parser import parse

from pycti import OpenCTIApiClient

# Variables
api_url = "http://localhost:4000"
api_token = "6C2C9EAE-6FF5-4421-B118-74A3CA5AAC20"

# OpenCTI initialization
opencti_api_client = OpenCTIApiClient(api_url, api_token)

# Define the date
date = parse("2019-02-06").strftime("%Y-%m-%dT%H:%M:%SZ")

process = opencti_api_client.stix_cyber_observable.create(
    observableData={
        "type": "Financial-Transaction",
        "transaction_date": date,
        "transaction_value": 62000000,
        "currency_code": "belarusian_ruble_(byr)",
    }
)

print(process)
