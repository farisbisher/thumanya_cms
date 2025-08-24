from celery import shared_task
from django.conf import settings
from kafka import KafkaProducer
import json
from cms.models import Program
from external_sources.youtube import YouTubeChannelSource

KAFKA_BOOTSTRAP = settings.KAFKA_BOOTSTRAP
KAFKA_TOPIC = "programs.events"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

@shared_task
def import_external_programs():
    """
    Import programs from all external sources.
    """
    # Example: YouTube import
    youtube_source = YouTubeChannelSource(channel_id="YOUR_CHANNEL_ID", api_key="YOUR_API_KEY")
    programs = youtube_source.fetch_programs()

    for p in programs:
        # Deduplication: avoid duplicates based on media_url
        obj, created = Program.objects.update_or_create(
            media_url=p["media_url"],
            defaults=p
        )

        # Produce Kafka event for discovery
        producer.send(KAFKA_TOPIC, {
            "action": "upsert",
            "data": {
                "id": obj.id,
                "title": obj.title,
                "description": obj.description,
                "category": obj.category,
                "language": obj.language,
                "duration": obj.duration,
                "publish_date": str(obj.publish_date),
                "media_type": obj.media_type,
                "media_url": obj.media_url,
                "thumbnail_url": obj.thumbnail_url,
                "metadata": obj.metadata,
                "created_at": str(obj.created_at),
                "updated_at": str(obj.updated_at)
            }
        })
    producer.flush()
    return f"Imported {len(programs)} programs."
