
import pytest
import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms_system.test_settings')
django.setup()

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Setup database for tests"""
    with django_db_blocker.unblock():
        from django.core.management import call_command
        call_command('migrate')

@pytest.fixture(autouse=True)
def clean_database(django_db_blocker):
    """Clean database before each test"""
    with django_db_blocker.unblock():
        from django.core.management import call_command
        # Clear all data from the database
        call_command('flush', '--noinput')
        # Run migrations to ensure clean state
        call_command('migrate')

@pytest.fixture
def api_client():
    """API client for testing"""
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def user():
    """Create a test user"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User',
        role='viewer'
    )

@pytest.fixture
def admin_user():
    """Create an admin user"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User',
        role='admin',
        is_staff=True
    )

@pytest.fixture
def editor_user():
    """Create an editor user"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        email='editor@example.com',
        password='editorpass123',
        first_name='Editor',
        last_name='User',
        role='editor'
    )

@pytest.fixture
def authenticated_client(api_client, user):
    """Authenticated API client"""
    from rest_framework.authtoken.models import Token
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return api_client

@pytest.fixture
def admin_client(api_client, admin_user):
    """Admin authenticated API client"""
    from rest_framework.authtoken.models import Token
    token = Token.objects.create(user=admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return api_client

# Discovery module fixtures
@pytest.fixture
def mock_opensearch_client():
    """Mock OpenSearch client for testing"""
    with pytest.Mock() as mock_client:
        # Mock cluster health
        mock_client.cluster.health.return_value = {'status': 'green'}
        # Mock index operations
        mock_client.indices.exists.return_value = False
        mock_client.indices.create.return_value = {'acknowledged': True}
        # Mock search operations
        mock_client.search.return_value = {
            'hits': {'total': {'value': 0}, 'hits': []},
            'took': 5,
            'aggregations': {}
        }
        yield mock_client

@pytest.fixture
def mock_kafka_consumer():
    """Mock Kafka consumer for testing"""
    with pytest.Mock() as mock_consumer:
        mock_consumer.__iter__.return_value = []
        yield mock_consumer

@pytest.fixture
def sample_program_data():
    """Sample program data for testing"""
    return {
        'id': 1,
        'title': 'Test Program',
        'description': 'A test program for testing',
        'category': 'Technology',
        'language': 'English',
        'duration': '0:30:00',
        'publish_date': '2024-01-01',
        'media_type': 'video',
        'media_url': 'https://example.com/video',
        'thumbnail_url': 'https://example.com/thumb.jpg',
        'metadata': {
            'tags': ['test', 'technology'],
            'guests': ['Test Guest'],
            'topics': ['Testing']
        },
        'created_at': '2024-01-01T00:00:00Z',
        'updated_at': '2024-01-01T00:00:00Z'
    }

@pytest.fixture
def sample_search_response():
    """Sample search response for testing"""
    return {
        'hits': {
            'total': {'value': 1},
            'hits': [
                {
                    '_source': {
                        'id': 1,
                        'title': 'Test Program',
                        'description': 'A test program',
                        'category': 'Technology',
                        'language': 'English',
                        'duration': '0:30:00',
                        'publish_date': '2024-01-01',
                        'media_type': 'video',
                        'media_url': 'https://example.com/video',
                        'thumbnail_url': 'https://example.com/thumb.jpg',
                        'metadata': {'tags': ['test']},
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z'
                    },
                    '_score': 0.95,
                    'highlight': {
                        'title': ['<em>Test</em> Program']
                    }
                }
            ]
        },
        'took': 5,
        'aggregations': {
            'categories': {'buckets': [{'key': 'Technology', 'doc_count': 1}]},
            'languages': {'buckets': [{'key': 'English', 'doc_count': 1}]},
            'media_types': {'buckets': [{'key': 'video', 'doc_count': 1}]}
        }
    }