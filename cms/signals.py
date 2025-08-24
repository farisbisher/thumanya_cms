from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
from .models import Category
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Program
import json
import os
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)

def get_kafka_producer():
    """Get Kafka producer instance"""
    try:
        kafka_bootstrap = os.environ.get('KAFKA_BOOTSTRAP', 'kafka:9092')
        producer = KafkaProducer(
            bootstrap_servers=[kafka_bootstrap],
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            retries=3
        )
        return producer
    except Exception as e:
        logger.error(f"Failed to create Kafka producer: {e}")
        return None

@receiver(post_save, sender=Program)
def send_program_to_kafka(sender, instance, created, **kwargs):
    """Send program data to Kafka when created/updated"""
    try:
        producer = get_kafka_producer()
        if producer is None:
            logger.error("Kafka producer not available")
            return

        # Prepare program data
        program_data = {
            "op": "upsert" if created else "update",
            "program_id": instance.id,
            "payload": {
                "id": instance.id,
                "title": instance.title,
                "description": instance.description,
                "category": instance.category.name if instance.category else None,
                "language": instance.language,
                "duration": str(instance.duration),
                "publish_date": instance.publish_date.isoformat(),
                "media_type": instance.media_type,
                "media_url": instance.media_url,
                "thumbnail_url": instance.thumbnail_url,
                "metadata": instance.metadata,
                "created_at": instance.created_at.isoformat(),
                "updated_at": instance.updated_at.isoformat()
            }
        }

        # Send to Kafka
        producer.send('programs.events', program_data)
        producer.flush()
        
        logger.info(f"Sent program to Kafka: {instance.title} (ID: {instance.id})")
        
    except Exception as e:
        logger.error(f"Error sending program to Kafka: {e}")

@receiver(post_delete, sender=Program)
def send_program_deletion_to_kafka(sender, instance, **kwargs):
    """Send program deletion event to Kafka"""
    try:
        producer = get_kafka_producer()
        if producer is None:
            logger.error("Kafka producer not available")
            return

        # Prepare deletion data
        deletion_data = {
            "op": "delete",
            "program_id": instance.id,
            "payload": {}
        }

        # Send to Kafka
        producer.send('programs.events', deletion_data)
        producer.flush()
        
        logger.info(f"Sent program deletion to Kafka: ID {instance.id}")
        
    except Exception as e:
        logger.error(f"Error sending program deletion to Kafka: {e}")


@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    """
    Create default categories after database migrations.
    This ensures the CMS has basic categories available.
    """
    # Skip if signals are disabled (e.g., during tests)
    from django.conf import settings
    if getattr(settings, 'SIGNALS_DISABLED', False):
        return
        
    # Only run this for the cms app
    if sender.name == 'cms':
        # Default categories for a CMS system
        default_categories = [
            {
                'name': 'Technology',
                'description': 'Technology and innovation content including software, hardware, and digital trends.'
            },
            {
                'name': 'Science',
                'description': 'Scientific discoveries, research, and educational content across all scientific fields.'
            },
            {
                'name': 'Business',
                'description': 'Business news, entrepreneurship, management, and economic insights.'
            },
            {
                'name': 'Health & Wellness',
                'description': 'Health tips, medical information, fitness, and wellness advice.'
            },
            {
                'name': 'Education',
                'description': 'Educational content, tutorials, courses, and learning resources.'
            },
            {
                'name': 'Entertainment',
                'description': 'Movies, TV shows, music, games, and entertainment industry content.'
            },
            {
                'name': 'News & Politics',
                'description': 'Current events, political analysis, and world news coverage.'
            },
            {
                'name': 'Lifestyle',
                'description': 'Fashion, travel, food, home improvement, and lifestyle content.'
            },
            {
                'name': 'Sports',
                'description': 'Sports news, analysis, highlights, and athletic content.'
            },
            {
                'name': 'Arts & Culture',
                'description': 'Art, literature, theater, museums, and cultural content.'
            }
        ]
        
        # Create categories if they don't exist
        for category_data in default_categories:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description']
                }
            )
            
            if created:
                print(f"Created category: {category.name}")
            else:
                print(f"Category already exists: {category.name}")
