import csv
import json
import os

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import DiscoveryV1

environment_id = "26e276ef-e35e-4076-a190-bab90b5a4521"
collection_id = "d954d9f6-d52c-40af-b8d0-148fbdceb49e"
service_url = "https://api.us-south.discovery.watson.cloud.ibm.com/instances/230365e2-48ca-4b2f-8a9e-3dba5fbe20ed"

apikey = "L8vZ5k9U8L8r8r9YstxDbOml0imvZBYmj7bB_tiVQ2GS"

authenticator = IAMAuthenticator(apikey)
discovery = DiscoveryV1(version="2019-04-30", authenticator=authenticator)
discovery.set_service_url(service_url)


def upload():
    with open("date-reviews.csv") as file:
        reader = csv.reader(file)

        next(reader)  # skips headers

        for name, review in reader:
            data = {"name": name, "text": review}
            tmp_name = "tmp.json"

            with open(tmp_name, "w+") as fp:
                json.dump(data, fp)
                fp.seek(0)
                add_doc = discovery.add_document(
                    environment_id, collection_id, file=fp
                ).get_result()
                print(add_doc)

            os.remove(tmp_name)


if __name__ == "__main__":
    print("Already uploaded.")
