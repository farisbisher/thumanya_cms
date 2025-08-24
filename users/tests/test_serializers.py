"""
Unit tests for User serializers
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
@pytest.mark.serializers
class TestUserSerializer:
    """Test cases for User serializers"""
    
    def test_user_serializer_fields(self, user):
        """Test UserSerializer includes correct fields"""
        from users.serializers import UserSerializer
        serializer = UserSerializer(user)
        data = serializer.data
        
        expected_fields = ['id', 'email', 'first_name', 'last_name', 'role', 'date_joined', 'is_active']
        for field in expected_fields:
            assert field in data
        
        # Password should not be included
        assert 'password' not in data
    
    def test_register_serializer_valid_data(self):
        """Test RegisterSerializer with valid data"""
        from users.serializers import RegisterSerializer
        
        data = {
            'email': 'new@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        serializer = RegisterSerializer(data=data)
        
        assert serializer.is_valid() is True
        user = serializer.save()
        
        assert user.email == 'new@example.com'
        assert user.first_name == 'New'
        assert user.last_name == 'User'
        assert user.check_password('newpass123') is True
        assert user.role == 'viewer'  # Default role
    
    def test_register_serializer_missing_fields(self):
        """Test RegisterSerializer validation with missing fields"""
        from users.serializers import RegisterSerializer
        
        serializer = RegisterSerializer(data={})
        
        assert serializer.is_valid() is False
        assert 'email' in serializer.errors
        assert 'password' in serializer.errors
    
    def test_register_serializer_invalid_email(self):
        """Test RegisterSerializer with invalid email"""
        from users.serializers import RegisterSerializer
        
        serializer = RegisterSerializer(data={
            'email': 'invalid-email',
            'password': 'testpass123'
        })
        
        assert serializer.is_valid() is False
        assert 'email' in serializer.errors
    
    def test_register_serializer_duplicate_email(self, user):
        """Test RegisterSerializer with duplicate email"""
        from users.serializers import RegisterSerializer
        
        serializer = RegisterSerializer(data={
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        
        assert serializer.is_valid() is False
        assert 'email' in serializer.errors
    
    def test_register_serializer_admin_role_override(self):
        """Test that RegisterSerializer prevents admin role registration"""
        from users.serializers import RegisterSerializer
        
        data = {
            'email': 'admin@example.com',
            'password': 'adminpass123',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin'  # This should be overridden to 'viewer'
        }
        serializer = RegisterSerializer(data=data)
        
        assert serializer.is_valid() is True
        user = serializer.save()
        
        # Should be overridden to viewer
        assert user.role == 'viewer'
    
    def test_login_serializer_valid_credentials(self, user):
        """Test LoginSerializer with valid credentials"""
        from users.serializers import LoginSerializer
        
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        serializer = LoginSerializer(data=data)
        
        assert serializer.is_valid() is True
        assert 'user' in serializer.validated_data
        assert serializer.validated_data['user'] == user
    
    def test_login_serializer_invalid_credentials(self):
        """Test LoginSerializer with invalid credentials"""
        from users.serializers import LoginSerializer
        
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        serializer = LoginSerializer(data=data)
        
        assert serializer.is_valid() is False
        assert 'non_field_errors' in serializer.errors
    
    def test_login_serializer_inactive_user(self):
        """Test LoginSerializer with inactive user"""
        from users.serializers import LoginSerializer
        
        # Create inactive user
        user = User.objects.create_user(
            email='inactive@example.com',
            password='testpass123',
            is_active=False
        )
        
        data = {
            'email': 'inactive@example.com',
            'password': 'testpass123'
        }
        serializer = LoginSerializer(data=data)
        
        assert serializer.is_valid() is False
        assert 'non_field_errors' in serializer.errors 