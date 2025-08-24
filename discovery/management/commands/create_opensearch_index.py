from django.core.management.base import BaseCommand
from django.conf import settings
import json
import os
from opensearchpy import OpenSearch

OPENSEARCH_HOST = getattr(settings, "OPENSEARCH_HOST", "opensearch:9200")
INDEX_NAME = getattr(settings, "DISCOVERY_INDEX_NAME", "programs")


def get_client():
    host, port = OPENSEARCH_HOST.split(":")
    return OpenSearch([{"host": host, "port": int(port)}], use_ssl=False, verify_certs=False)


class Command(BaseCommand):
    help = "Create OpenSearch index for discovery from opensearch/mapping_programs.json"

    def handle(self, *args, **options):
        mapping_path = os.path.join(settings.BASE_DIR, "opensearch", "mapping_programs.json")
        if not os.path.exists(mapping_path):
            self.stderr.write("Mapping file not found: %s" % mapping_path)
            return

        with open(mapping_path, "r", encoding="utf-8") as f:
            mapping = json.load(f)

        client = get_client()
        if client.indices.exists(index=INDEX_NAME):
            self.stdout.write("Index %s already exists. Deleting and recreating." % INDEX_NAME)
            client.indices.delete(index=INDEX_NAME)

        client.indices.create(index=INDEX_NAME, body=mapping)
        self.stdout.write(self.style.SUCCESS("Created index %s" % INDEX_NAME))
