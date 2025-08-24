"""
Unit tests for CMS module models
"""
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from cms.models import Category, Program

@pytest.mark.django_db
@pytest.mark.models
class TestCategoryModel:
    """Test cases for Category model"""
    
    def test_create_category(self):
        """Test creating a category"""
        # Use a unique name to avoid conflicts with existing data
        category = Category.objects.create(
            name="Test Technology Category",
            description="Technology and innovation content"
        )
        
        assert category.name == "Test Technology Category"
        assert category.description == "Technology and innovation content"
        assert str(category) == "Test Technology Category"
    
    def test_category_unique_name(self):
        """Test that category names must be unique"""
        # Create first category with unique name
        Category.objects.create(name="Unique Science Category", description="Scientific content")
        
        # Try to create duplicate - should fail
        with pytest.raises(Exception):  # IntegrityError
            Category.objects.create(name="Unique Science Category", description="Another science category")
    
    def test_category_blank_description(self):
        """Test creating category with blank description"""
        category = Category.objects.create(name="Test News Category")
        
        assert category.name == "Test News Category"
        assert category.description == ""

@pytest.mark.django_db
@pytest.mark.models
class TestProgramModel:
    """Test cases for Program model"""
    
    @pytest.fixture
    def category(self):
        """Create a test category with unique name"""
        return Category.objects.create(
            name="Test Category for Programs",
            description="Technology content"
        )
    
    def test_create_program(self, category):
        """Test creating a program"""
        program = Program.objects.create(
            title="Test Program",
            description="A test program description",
            category=category,
            language="English",
            duration=timedelta(hours=1, minutes=30),
            publish_date=timezone.now().date(),
            media_type="podcast",
            media_url="https://example.com/video.mp4"
        )
        
        assert program.title == "Test Program"
        assert program.category == category
        assert program.language == "English"
        assert program.media_type == "podcast"
        assert str(program) == "Test Program"
    
    def test_program_without_category(self):
        """Test creating a program without category"""
        program = Program.objects.create(
            title="Test Program No Category",
            description="A test program description",
            language="English",
            duration=timedelta(hours=1),
            publish_date=timezone.now().date(),
            media_type="documentary",
            media_url="https://example.com/video.mp4"
        )
        
        assert program.category is None
        assert program.title == "Test Program No Category"
    
    def test_program_media_types(self, category):
        """Test all valid media types"""
        for media_type in ["podcast", "documentary", "show", "other"]:
            program = Program.objects.create(
                title=f"Test {media_type} program",
                description="Test description",
                category=category,
                language="English",
                duration=timedelta(hours=1),
                publish_date=timezone.now().date(),
                media_type=media_type,
                media_url="https://example.com/video.mp4"
            )
            assert program.media_type == media_type
    
    def test_program_metadata_json(self, category):
        """Test program with JSON metadata"""
        metadata = {
            "guests": ["John Doe", "Jane Smith"],
            "tags": ["technology", "innovation"],
            "rating": 4.5
        }
        
        program = Program.objects.create(
            title="Test Program with Metadata",
            description="A test program description",
            category=category,
            language="English",
            duration=timedelta(hours=1),
            publish_date=timezone.now().date(),
            media_type="show",
            media_url="https://example.com/video.mp4",
            metadata=metadata
        )
        
        assert program.metadata == metadata
        assert program.metadata["guests"] == ["John Doe", "Jane Smith"]
    
    def test_program_thumbnail_url(self, category):
        """Test program with thumbnail URL"""
        program = Program.objects.create(
            title="Test Program with Thumbnail",
            description="A test program description",
            category=category,
            language="English",
            duration=timedelta(hours=1),
            publish_date=timezone.now().date(),
            media_type="documentary",
            media_url="https://example.com/video.mp4",
            thumbnail_url="https://example.com/thumbnail.jpg"
        )
        
        assert program.thumbnail_url == "https://example.com/thumbnail.jpg"
    
    def test_program_timestamps(self, category):
        """Test that created_at and updated_at are set automatically"""
        program = Program.objects.create(
            title="Test Program Timestamps",
            description="A test program description",
            category=category,
            language="English",
            duration=timedelta(hours=1),
            publish_date=timezone.now().date(),
            media_type="podcast",
            media_url="https://example.com/video.mp4"
        )
        
        assert program.created_at is not None
        assert program.updated_at is not None
        assert program.created_at <= timezone.now()
        assert program.updated_at <= timezone.now() 