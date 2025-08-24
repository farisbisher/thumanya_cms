import json
import logging
import os
import time
import sys

from kafka import KafkaConsumer
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests.exceptions import RequestException

LOG = logging.getLogger("discovery.indexer")
LOG.setLevel(logging.INFO)

# Add console handler for better logging
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
LOG.addHandler(console_handler)

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "opensearch:9200")
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "programs.events")
INDEX_NAME = os.getenv("DISCOVERY_INDEX_NAME", "programs")

def wait_for_opensearch(max_retries=60, retry_delay=5):
    """Wait for OpenSearch to be ready"""
    LOG.info(f"Waiting for OpenSearch at {OPENSEARCH_HOST} to be ready...")
    
    for attempt in range(max_retries):
        try:
            client = get_opensearch_client()
            # Try to get cluster health
            health = client.cluster.health()
            if health['status'] in ['green', 'yellow']:
                LOG.info(f"OpenSearch is ready! Cluster status: {health['status']}")
                return client
            else:
                LOG.info(f"OpenSearch is starting... Cluster status: {health['status']}")
        except Exception as e:
            LOG.info(f"Attempt {attempt + 1}/{max_retries}: OpenSearch not ready yet: {e}")
        
        if attempt < max_retries - 1:
            LOG.info(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    raise Exception(f"OpenSearch failed to become ready after {max_retries} attempts")

def get_opensearch_client():
    host, port = OPENSEARCH_HOST.split(":")
    client = OpenSearch(
        hosts=[{"host": host, "port": int(port)}],
        use_ssl=False,
        verify_certs=False,
        connection_class=RequestsHttpConnection,
        timeout=30,
        max_retries=3,
        retry_on_timeout=True
    )
    return client

def create_index_if_not_exists(client):
    """Create the programs index if it doesn't exist"""
    try:
        if not client.indices.exists(index=INDEX_NAME):
            client.indices.create(
                index=INDEX_NAME,
                body={
                    "mappings": {
                        "properties": {
                            "id": {"type": "integer"},
                            "title": {"type": "text", "analyzer": "standard"},
                            "description": {"type": "text", "analyzer": "standard"},
                            "category": {"type": "keyword"},
                            "language": {"type": "keyword"},
                            "duration": {"type": "keyword"},
                            "publish_date": {"type": "date"},
                            "media_type": {"type": "keyword"},
                            "media_url": {"type": "keyword"},
                            "thumbnail_url": {"type": "keyword"},
                            "metadata": {"type": "object"},
                            "created_at": {"type": "date"},
                            "updated_at": {"type": "date"}
                        }
                    },
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0
                    }
                }
            )
            LOG.info(f"Created index: {INDEX_NAME}")
        else:
            LOG.info(f"Index {INDEX_NAME} already exists")
    except Exception as e:
        LOG.error(f"Error creating index: {e}")
        raise

def handle_upsert(client, doc_id, payload):
    """Handle program upsert/update"""
    try:
        client.index(index=INDEX_NAME, id=doc_id, body=payload, refresh=True)
        LOG.info(f"Indexed program {doc_id}: {payload.get('title', 'Unknown')}")
    except Exception as e:
        LOG.error(f"Error indexing program {doc_id}: {e}")

def handle_delete(client, doc_id):
    """Handle program deletion"""
    try:
        client.delete(index=INDEX_NAME, id=doc_id, refresh=True)
        LOG.info(f"Deleted program {doc_id}")
    except Exception as e:
        LOG.warning(f"Delete failed for {doc_id}: {e}")

def run_consumer():
    LOG.info("Starting CMS Discovery Indexer...")
    LOG.info(f"Connecting to OpenSearch: {OPENSEARCH_HOST}")
    LOG.info(f"Connecting to Kafka: {KAFKA_BOOTSTRAP}")
    LOG.info(f"Listening to topic: {TOPIC}")
    
    # Wait for OpenSearch to be ready
    try:
        client = wait_for_opensearch()
        create_index_if_not_exists(client)
    except Exception as e:
        LOG.error(f"Failed to connect to OpenSearch: {e}")
        sys.exit(1)
    
    # Wait for Kafka to be ready
    LOG.info("Waiting for Kafka to be ready...")
    time.sleep(15)  # Give Kafka more time to fully start
    
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="discovery-indexer",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        consumer_timeout_ms=1000,
    )

    LOG.info("Kafka consumer created successfully")
    LOG.info("Starting to listen for messages...")

    while True:
        try:
            for message in consumer:
                try:
                    event = message.value
                    LOG.info(f"Received message: {event}")
                    
                    op = event.get("op")
                    program_id = event.get("program_id")
                    payload = event.get("payload", {})

                    if op in ("upsert", "create", "update"):
                        handle_upsert(client, program_id, payload)
                    elif op == "delete":
                        handle_delete(client, program_id)
                    else:
                        LOG.warning(f"Unknown operation: {op}")
                        
                except Exception as e:
                    LOG.exception("Error processing message: %s", e)

            time.sleep(0.5)
            
        except Exception as e:
            LOG.error(f"Consumer error: {e}")
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    run_consumer()
