"""
Unit tests for CMS module serializers
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from cms.models import Category, Program
from cms.serializers import CategorySerializer, ProgramSerializer

@pytest.mark.django_db
@pytest.mark.serializers
class TestCategorySerializer:
    """Test cases for CategorySerializer"""
    
    def test_category_serializer_valid_data(self):
        """Test CategorySerializer with valid data"""
        data = {
            'name': 'Test Technology Category',
            'description': 'Technology and innovation content'
        }
        
        serializer = CategorySerializer(data=data)
        assert serializer.is_valid()
        
        category = serializer.save()
        assert category.name == 'Test Technology Category'
        assert category.description == 'Technology and innovation content'
    
    def test_category_serializer_serialization(self):
        """Test CategorySerializer serialization"""
        category = Category.objects.create(
            name='Test Science Category',
            description='Scientific content'
        )
        
        serializer = CategorySerializer(category)
        data = serializer.data
        
        assert data['id'] == category.id
        assert data['name'] == 'Test Science Category'
        assert data['description'] == 'Scientific content'
    
    def test_category_serializer_validation(self):
        """Test CategorySerializer validation"""
        # Test missing name
        data = {'description': 'Test description'}
        serializer = CategorySerializer(data=data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors
    
    def test_category_serializer_update(self):
        """Test CategorySerializer update"""
        category = Category.objects.create(
            name='Test Old Name Category',
            description='Old description'
        )
        
        data = {
            'name': 'Test New Name Category',
            'description': 'New description'
        }
        
        serializer = CategorySerializer(category, data=data)
        assert serializer.is_valid()
        
        updated_category = serializer.save()
        assert updated_category.name == 'Test New Name Category'
        assert updated_category.description == 'New description'

@pytest.mark.django_db
@pytest.mark.serializers
class TestProgramSerializer:
    """Test cases for ProgramSerializer"""
    
    @pytest.fixture
    def category(self):
        """Create a test category"""
        return Category.objects.create(
            name='Test Technology Category',
            description='Technology content'
        )
    
    def test_program_serializer_valid_data(self, category):
        """Test ProgramSerializer with valid data"""
        data = {
            'title': 'Test Program',
            'description': 'A test program description',
            'category_id': category.id,
            'language': 'English',
            'duration': '01:30:00',
            'publish_date': '2024-01-15',
            'media_type': 'podcast',
            'media_url': 'https://example.com/video.mp4',
            'thumbnail_url': 'https://example.com/thumbnail.jpg',
            'metadata': {
                'guests': ['John Doe'],
                'tags': ['technology']
            }
        }
        
        serializer = ProgramSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        
        program = serializer.save()
        assert program.title == 'Test Program'
        assert program.category == category
        assert program.language == 'English'
        assert program.media_type == 'podcast'
    
    def test_program_serializer_serialization(self, category):
        """Test ProgramSerializer serialization"""
        program = Program.objects.create(
            title='Test Program',
            description='A test program description',
            category=category,
            language='English',
            duration=timedelta(hours=1, minutes=30),
            publish_date=timezone.now().date(),
            media_type='podcast',
            media_url='https://example.com/video.mp4',
            metadata={'tags': ['technology']}
        )
        
        serializer = ProgramSerializer(program)
        data = serializer.data
        
        assert data['id'] == program.id
        assert data['title'] == 'Test Program'
        assert data['category']['id'] == category.id
        assert data['category']['name'] == category.name
        assert data['language'] == 'English'
        assert data['media_type'] == 'podcast'
        assert data['metadata'] == {'tags': ['technology']}
        assert 'created_at' in data
        assert 'updated_at' in data
    
    def test_program_serializer_validation(self):
        """Test ProgramSerializer validation"""
        # Test missing required fields
        data = {'title': 'Test Program'}
        serializer = ProgramSerializer(data=data)
        assert not serializer.is_valid()
        assert 'description' in serializer.errors
        assert 'language' in serializer.errors
        assert 'duration' in serializer.errors
        assert 'publish_date' in serializer.errors
        assert 'media_url' in serializer.errors
    
    def test_program_serializer_invalid_media_type(self):
        """Test ProgramSerializer with invalid media type"""
        data = {
            'title': 'Test Program',
            'description': 'A test program description',
            'language': 'English',
            'duration': '01:30:00',
            'publish_date': '2024-01-15',
            'media_type': 'invalid_type',
            'media_url': 'https://example.com/video.mp4'
        }
        
        serializer = ProgramSerializer(data=data)
        assert not serializer.is_valid()
        assert 'media_type' in serializer.errors
    
    def test_program_serializer_read_only_fields(self, category):
        """Test that read-only fields are not updated"""
        program = Program.objects.create(
            title='Test Program',
            description='A test program description',
            category=category,
            language='English',
            duration=timedelta(hours=1),
            publish_date=timezone.now().date(),
            media_type='podcast',
            media_url='https://example.com/video.mp4'
        )
        
        original_created_at = program.created_at
        original_updated_at = program.updated_at
        
        data = {
            'title': 'Updated Program',
            'description': 'Updated description',
            'language': 'English',
            'duration': '01:00:00',
            'publish_date': '2024-01-15',
            'media_type': 'podcast',
            'media_url': 'https://example.com/video.mp4'
        }
        
        serializer = ProgramSerializer(program, data=data)
        assert serializer.is_valid()
        
        updated_program = serializer.save()
        assert updated_program.title == 'Updated Program'
        assert updated_program.created_at == original_created_at
        # updated_at should be different as it auto-updates
        assert updated_program.updated_at != original_updated_at 