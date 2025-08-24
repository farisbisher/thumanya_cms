"""
Unit tests for User model
"""
import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
@pytest.mark.models
class TestUserModel:
    """Test cases for User model"""
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        assert user.email == 'test@example.com'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'
        assert user.role == 'viewer'  # Default role
        assert user.is_active is True
        assert user.check_password('testpass123') is True
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        
        assert superuser.is_staff is True
        assert superuser.is_superuser is True
        assert superuser.role == 'admin'
    
    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        assert str(user) == 'test@example.com'
    
    def test_user_roles(self):
        """Test user role choices"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        # Test valid roles
        for role in ['admin', 'editor', 'viewer']:
            user.role = role
            user.full_clean()  # Should not raise ValidationError
        
        # Test invalid role
        with pytest.raises(ValidationError):
            user.role = 'invalid_role'
            user.full_clean()
    
    def test_email_required(self):
        """Test that email is required"""
        with pytest.raises(ValueError):
            User.objects.create_user(email='', password='testpass123')

    def test_user_permissions(self):
        """Test user permissions based on roles"""
        viewer = User.objects.create_user(
            email='viewer@example.com',
            password='testpass123',
            role='viewer'
        )
        editor = User.objects.create_user(
            email='editor@example.com',
            password='testpass123',
            role='editor'
        )
        admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            role='admin',
            is_staff=True
        )
        
        # Test that admin has staff permissions
        assert admin.is_staff is True
        
        # Test that viewer and editor don't have staff permissions by default
        assert viewer.is_staff is False
        assert editor.is_staff is False
    
    def test_user_properties(self):
        """Test user role properties"""
        admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            role='admin'
        )
        editor = User.objects.create_user(
            email='editor@example.com',
            password='testpass123',
            role='editor'
        )
        viewer = User.objects.create_user(
            email='viewer@example.com',
            password='testpass123',
            role='viewer'
        )
        
        # Test is_admin property
        assert admin.is_admin is True
        assert editor.is_admin is False
        assert viewer.is_admin is False
        
        # Test is_editor property
        assert admin.is_editor is True
        assert editor.is_editor is True
        assert viewer.is_editor is False
        
        # Test is_viewer property (all users are viewers)
        assert admin.is_viewer is True
        assert editor.is_viewer is True
        assert viewer.is_viewer is True 