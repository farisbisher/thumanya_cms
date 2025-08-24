"""
Unit tests for CMS module views
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
@pytest.mark.views
class TestCMSViews:
    """Test cases for CMS views"""
    
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
    
    @pytest.fixture
    def category(self):
        """Create a test category"""
        return Category.objects.create(
            name='Test Technology Category',
            description='Technology content'
        )
    
    @pytest.fixture
    def program(self, category):
        """Create a test program"""
        return Program.objects.create(
            title='Test Program',
            description='A test program description',
            category=category,
            language='English',
            duration=timedelta(hours=1, minutes=30),
            publish_date=timezone.now().date(),
            media_type='podcast',
            media_url='https://example.com/video.mp4'
        )
    
    def test_index_view(self, api_client):
        """Test the CMS index view"""
        response = api_client.get('/api/cms/')
        assert response.status_code == 200
        assert "CMS Module - Welcome" in response.content.decode()
    
    def test_program_list_view_authenticated(self, api_client, user):
        """Test program list view for authenticated user"""
        api_client.force_authenticate(user=user)
        response = api_client.get('/api/cms/programs/')
        assert response.status_code == 200
    
    def test_program_list_view_unauthenticated(self, api_client):
        """Test program list view for unauthenticated user"""
        response = api_client.get('/api/cms/programs/')
        assert response.status_code == 401
    
    def test_program_create_view_authenticated(self, api_client, user, category):
        """Test program creation for authenticated user"""
        api_client.force_authenticate(user=user)
        
        data = {
            'title': 'New Program',
            'description': 'A new program description',
            'category_id': category.id,
            'language': 'English',
            'duration': '01:30:00',
            'publish_date': '2024-01-15',
            'media_type': 'podcast',
            'media_url': 'https://example.com/video.mp4'
        }
        
        response = api_client.post('/api/cms/programs/', data)
        assert response.status_code == 201
        assert response.data['title'] == 'New Program'
    
    def test_program_detail_view(self, api_client, user, program):
        """Test program detail view"""
        api_client.force_authenticate(user=user)
        response = api_client.get(f'/api/cms/programs/{program.id}/')
        assert response.status_code == 200
        assert response.data['title'] == 'Test Program'
    
    def test_program_update_view(self, api_client, user, program):
        """Test program update view"""
        api_client.force_authenticate(user=user)
        
        data = {
            'title': 'Updated Program',
            'description': 'Updated description',
            'language': 'English',
            'duration': '01:00:00',
            'publish_date': '2024-01-15',
            'media_type': 'podcast',
            'media_url': 'https://example.com/video.mp4'
        }
        
        response = api_client.put(f'/api/cms/programs/{program.id}/', data)
        assert response.status_code == 200
        assert response.data['title'] == 'Updated Program'
    
    def test_program_delete_view(self, api_client, user, program):
        """Test program delete view"""
        api_client.force_authenticate(user=user)
        response = api_client.delete(f'/api/cms/programs/{program.id}/')
        assert response.status_code == 204
    
    def test_program_by_category_view(self, api_client, user, category, program):
        """Test program filtering by category"""
        api_client.force_authenticate(user=user)
        response = api_client.get(f'/api/cms/programs/by_category/?category={category.name}')
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['title'] == 'Test Program'
    
    def test_program_by_category_view_no_category(self, api_client, user):
        """Test program filtering by category with no category parameter"""
        api_client.force_authenticate(user=user)
        response = api_client.get('/api/cms/programs/by_category/')
        assert response.status_code == 200
    
    def test_category_list_view_authenticated(self, api_client, user):
        """Test category list view for authenticated user"""
        api_client.force_authenticate(user=user)
        response = api_client.get('/api/cms/categories/')
        assert response.status_code == 200
    
    def test_category_list_view_unauthenticated(self, api_client):
        """Test category list view for unauthenticated user"""
        response = api_client.get('/api/cms/categories/')
        assert response.status_code == 401
    
    def test_category_create_view(self, api_client, user):
        """Test category creation"""
        api_client.force_authenticate(user=user)
        
        data = {
            'name': 'New Test Category',
            'description': 'A new category description'
        }
        
        response = api_client.post('/api/cms/categories/', data)
        assert response.status_code == 201
        assert response.data['name'] == 'New Test Category'
    
    def test_category_detail_view(self, api_client, user, category):
        """Test category detail view"""
        api_client.force_authenticate(user=user)
        response = api_client.get(f'/api/cms/categories/{category.id}/')
        assert response.status_code == 200
        assert response.data['name'] == 'Test Technology Category'
    
    def test_category_update_view(self, api_client, user, category):
        """Test category update view"""
        api_client.force_authenticate(user=user)
        
        data = {
            'name': 'Updated Test Category',
            'description': 'Updated category description'
        }
        
        response = api_client.put(f'/api/cms/categories/{category.id}/', data)
        assert response.status_code == 200
        assert response.data['name'] == 'Updated Test Category'
    
    def test_category_delete_view(self, api_client, user, category):
        """Test category delete view"""
        api_client.force_authenticate(user=user)
        response = api_client.delete(f'/api/cms/categories/{category.id}/')
        assert response.status_code == 204
    
    def test_program_not_found(self, api_client, user):
        """Test accessing non-existent program"""
        api_client.force_authenticate(user=user)
        response = api_client.get('/api/cms/programs/999/')
        assert response.status_code == 404
    
    def test_category_not_found(self, api_client, user):
        """Test accessing non-existent category"""
        api_client.force_authenticate(user=user)
        response = api_client.get('/api/cms/categories/999/')
        assert response.status_code == 404 