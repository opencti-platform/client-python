# coding: utf-8

from pycti import OpenCTIApiClient

# Variables
api_url = "http://localhost:4000"
api_token = "6C2C9EAE-6FF5-4421-B118-74A3CA5AAC20"

# OpenCTI initialization
opencti_api_client = OpenCTIApiClient(api_url, api_token)

process = opencti_api_client.stix_cyber_observable.create(
    observableData={
        "type": "Financial-Asset",
        "asset_name": "Joe's Big Boat",
        "asset_type": "boat",
        "asset_value": 12000000,
        "currency_code": "belarusian_ruble_(byr)",
    }
)

print(process)
