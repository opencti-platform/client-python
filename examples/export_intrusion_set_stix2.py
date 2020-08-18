# coding: utf-8

import json
from pycti import OpenCTIApiClient

# Variables
api_url = "https://demo.opencti.io"
api_token = "2b4f29e3-5ea8-4890-8cf5-a76f61f1e2b2"

# OpenCTI initialization
opencti_api_client = OpenCTIApiClient(api_url, api_token)

# Create the bundle
bundle = opencti_api_client.stix2.export_entity(
    "Intrusion-Set", "4ecc2f52-d10a-4e10-bb9b-1ab5df2b282e", "full"
)
json_bundle = json.dumps(bundle, indent=4)

# Write the bundle
f = open("intrusion-set.json", "w")
f.write(json_bundle)
f.close()
