"""
Unit tests for Discovery module serializers
"""
import pytest
from datetime import date

@pytest.mark.django_db
@pytest.mark.serializers
class TestDiscoverySerializers:
    """Test cases for Discovery serializers"""
    
    def test_program_search_result_serializer_valid_data(self):
        """Test ProgramSearchResultSerializer with valid data"""
        from discovery.serializers import ProgramSearchResultSerializer
        
        data = {
            'program_id': '123',
            'title': 'Test Program',
            'description': 'A test program description',
            'category': 'Technology',
            'language': 'English',
            'media_type': 'video',
            'media_url': 'https://example.com/video',
            'thumbnail_url': 'https://example.com/thumb.jpg',
            'duration_seconds': 1800,
            'publish_date': '2024-01-01',
            'score': 0.95
        }
        
        serializer = ProgramSearchResultSerializer(data=data)
        assert serializer.is_valid() is True
        
        # Test serialized data
        serialized_data = serializer.data
        assert serialized_data['program_id'] == '123'
        assert serialized_data['title'] == 'Test Program'
        assert serialized_data['description'] == 'A test program description'
        assert serialized_data['category'] == 'Technology'
        assert serialized_data['language'] == 'English'
        assert serialized_data['media_type'] == 'video'
        assert serialized_data['media_url'] == 'https://example.com/video'
        assert serialized_data['thumbnail_url'] == 'https://example.com/thumb.jpg'
        assert serialized_data['duration_seconds'] == 1800
        assert serialized_data['publish_date'] == '2024-01-01'
        assert serialized_data['score'] == 0.95
    
    def test_program_search_result_serializer_missing_optional_fields(self):
        """Test ProgramSearchResultSerializer with missing optional fields"""
        from discovery.serializers import ProgramSearchResultSerializer
        
        data = {
            'program_id': '123',
            'score': 0.95
            # Missing optional fields should be allowed
        }
        
        serializer = ProgramSearchResultSerializer(data=data)
        assert serializer.is_valid() is True
        
        # Test that optional fields are None
        serialized_data = serializer.data
        assert serialized_data['title'] is None
        assert serialized_data['description'] is None
        assert serialized_data['category'] is None
        assert serialized_data['language'] is None
        assert serialized_data['media_type'] is None
        assert serialized_data['media_url'] is None
        assert serialized_data['thumbnail_url'] is None
        assert serialized_data['duration_seconds'] is None
        assert serialized_data['publish_date'] is None
    
    def test_program_search_result_serializer_missing_required_fields(self):
        """Test ProgramSearchResultSerializer with missing required fields"""
        from discovery.serializers import ProgramSearchResultSerializer
        
        # Missing program_id (required)
        data = {
            'title': 'Test Program',
            'score': 0.95
        }
        
        serializer = ProgramSearchResultSerializer(data=data)
        assert serializer.is_valid() is False
        assert 'program_id' in serializer.errors
        
        # Missing score (required)
        data = {
            'program_id': '123',
            'title': 'Test Program'
        }
        
        serializer = ProgramSearchResultSerializer(data=data)
        assert serializer.is_valid() is False
        assert 'score' in serializer.errors
    
    def test_program_search_result_serializer_invalid_data_types(self):
        """Test ProgramSearchResultSerializer with invalid data types"""
        from discovery.serializers import ProgramSearchResultSerializer
        
        data = {
            'program_id': '123',  # String is valid
            'duration_seconds': 'invalid',  # Should be integer
            'score': 'high',  # Should be float
            'publish_date': 'invalid-date'  # Should be valid date
        }
        
        serializer = ProgramSearchResultSerializer(data=data)
        assert serializer.is_valid() is False
        # program_id is actually valid as string, so it won't be in errors
        assert 'duration_seconds' in serializer.errors
        assert 'score' in serializer.errors
        assert 'publish_date' in serializer.errors
    

    def test_program_search_result_serializer_debug(self):
        """Debug test to see what validation errors occur"""
        from discovery.serializers import ProgramSearchResultSerializer
        
        # Test the data that's failing
        data = {
            'program_id': '123',
            'score': 0.95
        }
        
        serializer = ProgramSearchResultSerializer(data=data)
        print(f"Validation result: {serializer.is_valid()}")
        if not serializer.is_valid():
            print(f"Validation errors: {serializer.errors}")
        
        # Test the other failing data
        data2 = {
            'program_id': '123',
            'title': '',
            'description': '',
            'score': 0.0
        }
        
        serializer2 = ProgramSearchResultSerializer(data=data2)
        print(f"Validation result 2: {serializer2.is_valid()}")
        if not serializer2.is_valid():
            print(f"Validation errors 2: {serializer2.errors}")
        
        # This test should pass to show the debug output
        assert True
