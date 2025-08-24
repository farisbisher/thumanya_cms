"""
Integration tests for CMS module
"""
import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from cms.models import Category, Program
from users.models import User

@pytest.mark.django_db
@pytest.mark.integration
class TestCMSIntegration:
    """Integration tests for CMS module"""
    
    @pytest.fixture
    def api_client(self):
        """Create API client"""
        return APIClient()
    
    @pytest.fixture
    def user(self):
        """Create a test user"""
        return User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='viewer'
        )
    
    @pytest.fixture
    def admin_user(self):
        """Create an admin user"""
        return User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
    
    def test_full_program_lifecycle(self, api_client, user):
        """Test complete program lifecycle: create, read, update, delete"""
        api_client.force_authenticate(user=user)
        
        # 1. Create category
        category_data = {
            'name': 'Integration Test Category',
            'description': 'Technology content'
        }
        category_response = api_client.post('/api/cms/categories/', category_data)
        assert category_response.status_code == 201
        category_id = category_response.data['id']
        
        # 2. Create program
        program_data = {
            'title': 'Integration Test Program',
            'description': 'A test program description',
            'category_id': category_id,
            'language': 'English',
            'duration': '01:30:00',
            'publish_date': '2024-01-15',
            'media_type': 'podcast',
            'media_url': 'https://example.com/video.mp4'
        }
        program_response = api_client.post('/api/cms/programs/', program_data)
        assert program_response.status_code == 201
        program_id = program_response.data['id']
        
        # 3. Read program
        read_response = api_client.get(f'/api/cms/programs/{program_id}/')
        assert read_response.status_code == 200
        assert read_response.data['title'] == 'Integration Test Program'
        assert read_response.data['category']['id'] == category_id
        
        # 4. Update program
        update_data = {
            'title': 'Updated Integration Program',
            'description': 'Updated description',
            'language': 'English',
            'duration': '01:00:00',
            'publish_date': '2024-01-15',
            'media_type': 'podcast',
            'media_url': 'https://example.com/video.mp4'
        }
        update_response = api_client.put(f'/api/cms/programs/{program_id}/', update_data)
        assert update_response.status_code == 200
        assert update_response.data['title'] == 'Updated Integration Program'
        
        # 5. Delete program
        delete_response = api_client.delete(f'/api/cms/programs/{program_id}/')
        assert delete_response.status_code == 204
        
        # 6. Verify program is deleted
        verify_response = api_client.get(f'/api/cms/programs/{program_id}/')
        assert verify_response.status_code == 404
    
    def test_category_program_relationship(self, api_client, user):
        """Test the relationship between categories and programs"""
        api_client.force_authenticate(user=user)
        
        # Create multiple categories
        tech_category = Category.objects.create(name='Integration Tech Category', description='Tech content')
        science_category = Category.objects.create(name='Integration Science Category', description='Science content')
        
        # Create programs in different categories
        tech_program = Program.objects.create(
            title='Integration Tech Program',
            description='Technology program',
            category=tech_category,
            language='English',
            duration=timedelta(hours=1),
            publish_date=timezone.now().date(),
            media_type='podcast',
            media_url='https://example.com/tech.mp4'
        )
        
        science_program = Program.objects.create(
            title='Integration Science Program',
            description='Science program',
            category=science_category,
            language='English',
            duration=timedelta(hours=1),
            publish_date=timezone.now().date(),
            media_type='documentary',
            media_url='https://example.com/science.mp4'
        )
        
        # Test filtering by category
        tech_response = api_client.get(f'/api/cms/programs/by_category/?category=Integration Tech Category')
        assert tech_response.status_code == 200
        assert len(tech_response.data) == 1
        assert tech_response.data[0]['title'] == 'Integration Tech Program'
        
        science_response = api_client.get(f'/api/cms/programs/by_category/?category=Integration Science Category')
        assert science_response.status_code == 200
        assert len(science_response.data) == 1
        assert science_response.data[0]['title'] == 'Integration Science Program'
        
        # Test category programs relationship
        tech_category.refresh_from_db()
        assert tech_category.programs.count() == 1
        assert tech_category.programs.first() == tech_program
    
    def test_program_metadata_integration(self, api_client, user):
        """Test program metadata handling in full workflow"""
        api_client.force_authenticate(user=user)
        
        category = Category.objects.create(name='Integration Metadata Category')
        
        # Create program with metadata
        program_data = {
            'title': 'Integration Program with Metadata',
            'description': 'A program with rich metadata',
            'category_id': category.id,
            'language': 'English',
            'duration': '01:00:00',
            'publish_date': '2024-01-15',
            'media_type': 'show',
            'media_url': 'https://example.com/video.mp4',
            'metadata': {
                'guests': ['John Doe', 'Jane Smith'],
                'tags': ['technology', 'innovation'],
                'rating': 4.5,
                'episode_number': 1
            }
        }
        
        create_response = api_client.post('/api/cms/programs/', program_data)
        assert create_response.status_code == 201
        program_id = create_response.data['id']
        
        # Verify metadata is stored correctly
        read_response = api_client.get(f'/api/cms/programs/{program_id}/')
        assert read_response.status_code == 200
        metadata = read_response.data['metadata']
        assert metadata['guests'] == ['John Doe', 'Jane Smith']
        assert metadata['tags'] == ['technology', 'innovation']
        assert metadata['rating'] == 4.5
        assert metadata['episode_number'] == 1
    
    def test_program_validation_integration(self, api_client, user):
        """Test program validation in real API calls"""
        api_client.force_authenticate(user=user)
        
        # Test invalid data
        invalid_data = {
            'title': '',  # Empty title
            'description': 'Test description',
            'language': 'English',
            'duration': 'invalid_duration',  # Invalid duration
            'publish_date': 'invalid_date',  # Invalid date
            'media_type': 'invalid_type',  # Invalid media type
            'media_url': 'not_a_url'  # Invalid URL
        }
        
        response = api_client.post('/api/cms/programs/', invalid_data)
        assert response.status_code == 400
        errors = response.data
        
        # Check that validation errors are returned
        assert 'title' in errors
        assert 'duration' in errors
        assert 'publish_date' in errors
        assert 'media_type' in errors
        assert 'media_url' in errors
    
    def test_category_uniqueness_integration(self, api_client, user):
        """Test category name uniqueness in API"""
        api_client.force_authenticate(user=user)
        
        # Create first category
        category_data = {
            'name': 'Integration Unique Category',
            'description': 'Technology content'
        }
        first_response = api_client.post('/api/cms/categories/', category_data)
        assert first_response.status_code == 201
        
        # Try to create duplicate category
        duplicate_data = {
            'name': 'Integration Unique Category',  # Same name
            'description': 'Different description'
        }
        duplicate_response = api_client.post('/api/cms/categories/', duplicate_data)
        assert duplicate_response.status_code == 400
        assert 'name' in duplicate_response.data
    
    def test_program_search_integration(self, api_client, user):
        """Test program search functionality"""
        api_client.force_authenticate(user=user)
        
        # Create test data
        category = Category.objects.create(name='Integration Search Category')
        
        programs = [
            Program.objects.create(
                title=f'Integration Search Program {i}',
                description=f'Description for program {i}',
                category=category,
                language='English',
                duration=timedelta(hours=1),
                publish_date=timezone.now().date(),
                media_type='podcast',
                media_url=f'https://example.com/program{i}.mp4'
            )
            for i in range(1, 4)
        ]
        
        # Test listing all programs
        list_response = api_client.get('/api/cms/programs/')
        assert list_response.status_code == 200
        assert len(list_response.data) >= 3  # At least our 3 programs
        
        # Test filtering by category
        filter_response = api_client.get('/api/cms/programs/by_category/?category=Integration Search Category')
        assert filter_response.status_code == 200
        assert len(filter_response.data) == 3
        
        # Test filtering by non-existent category
        empty_response = api_client.get('/api/cms/programs/by_category/?category=NonExistent')
        assert empty_response.status_code == 200
        assert len(empty_response.data) == 0 