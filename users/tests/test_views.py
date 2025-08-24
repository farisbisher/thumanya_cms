"""
Unit tests for User views
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

@pytest.mark.django_db
@pytest.mark.views
@pytest.mark.api
class TestUserViews:
    """Test cases for User views"""
    
    def test_register_view_success(self, api_client):
        """Test successful user registration"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = api_client.post(reverse('users:register'), data)
        
        assert response.status_code == status.HTTP_201_CREATED
        # Check that user data is returned (without id and token)
        assert response.data['email'] == 'test@example.com'
        assert response.data['first_name'] == 'Test'
        assert response.data['last_name'] == 'User'
        assert response.data['role'] == 'viewer'
        # Note: RegisterSerializer doesn't return id or token
    
    def test_register_view_duplicate_email(self, api_client, user):
        """Test registration with duplicate email"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = api_client.post(reverse('users:register'), data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_login_view_success(self, api_client, user):
        """Test successful user login"""
        response = api_client.post(reverse('users:login'), {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data
        assert 'user' in response.data
        assert response.data['user']['email'] == 'test@example.com'
    
    def test_login_view_invalid_credentials(self, api_client):
        """Test login with invalid credentials"""
        response = api_client.post(reverse('users:login'), {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data
    
    def test_logout_view_success(self, authenticated_client, user):
        """Test successful user logout"""
        response = authenticated_client.post(reverse('users:logout'))
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Logged out successfully'
        
        # Verify token was deleted
        with pytest.raises(Token.DoesNotExist):
            Token.objects.get(user=user)
    
    def test_profile_view_authenticated(self, authenticated_client, user):
        """Test getting user profile when authenticated"""
        response = authenticated_client.get(reverse('users:profile'))
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'test@example.com'
        assert response.data['first_name'] == 'Test'
        assert response.data['last_name'] == 'User'
    
    def test_profile_view_unauthenticated(self, api_client):
        """Test getting user profile when not authenticated"""
        response = api_client.get(reverse('users:profile'))
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
@pytest.mark.integration
class TestUserIntegration:
    """Integration test cases for User module"""
    
    def test_complete_user_workflow(self, api_client):
        """Test complete user registration, login, profile, logout workflow"""
        # 1. Register new user
        register_data = {
            'email': 'workflow@example.com',
            'password': 'workflow123',
            'first_name': 'Workflow',
            'last_name': 'User'
        }
        
        register_response = api_client.post(reverse('users:register'), register_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # 2. Login to get token
        login_response = api_client.post(reverse('users:login'), {
            'email': 'workflow@example.com',
            'password': 'workflow123'
        })
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.data['token']
        
        # 3. Get profile with token
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        profile_response = api_client.get(reverse('users:profile'))
        assert profile_response.status_code == status.HTTP_200_OK
        assert profile_response.data['email'] == 'workflow@example.com'
        
        # 4. Logout
        logout_response = api_client.post(reverse('users:logout'))
        assert logout_response.status_code == status.HTTP_200_OK
        
        # 5. Try to access profile after logout (should fail)
        profile_response = api_client.get(reverse('users:profile'))
        assert profile_response.status_code == status.HTTP_401_UNAUTHORIZED
