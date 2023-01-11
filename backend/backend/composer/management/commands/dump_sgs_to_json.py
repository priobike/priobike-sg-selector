import datetime
import requests
import json

from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from routing.models import LSA

class Command(BaseCommand):
    help = """
        Dumps all the sgs in the database to a .json file.
        This can be used when creating a ground truth dataset with the composer to prevent
        the leaking of new sgs into the dataset that could automatically get used as samples with the label "no match"
        although they did not get categorized appropriately. In detail one should load the sgs from the created .json-file
        instead of dynamically from the FROST-server.
    """
    
    def add_arguments(self, parser):
        parser.add_argument("--api", type=str)
        parser.add_argument("--filter", type=str)

    def handle(self, *args, **options):
        
        lsas = []
        
        url = f"{options['api']}/Things?$filter={options['filter']}&$expand=Locations,Datastreams"
        while True:
            print("Fetching data from directory:", url)
            response = requests.get(url)
            if response.status_code != 200:
                raise ValueError(f"Could not fetch LSA data from {url}")
            response_json = response.json()

            for thing_json in response_json["value"]:
                try:
                    lsas.append(thing_json)
                except Exception as e:
                    print(f"Could not create LSA {thing_json['name']}: {e}")
            
            url = response_json.get("@iot.nextLink")
            if not url:
                break

        with open(f"../data/sgs-{datetime.datetime.now().isoformat()}.json", "w") as f:
            json.dump(lsas, f)