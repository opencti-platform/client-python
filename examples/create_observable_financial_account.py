# coding: utf-8

from pycti import OpenCTIApiClient

# Variables
api_url = "http://localhost:4000"
api_token = "6C2C9EAE-6FF5-4421-B118-74A3CA5AAC20"

# OpenCTI initialization
opencti_api_client = OpenCTIApiClient(api_url, api_token)

process = opencti_api_client.stix_cyber_observable.create(
    observableData={
        "type": "Financial-Account",
        "account_number": "123-45-9988",
        "account_status": "active",
        "account_type": "credit_credit_card",
        "x_opencti_score": 90,
        "iban": "55667",
        "bic": "009998877",
        "currency_code": "bahraini_dinar_(bhd)",
    }
)

print(process)
