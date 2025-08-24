"""
Unit tests for Discovery module models
"""
import pytest
from django.test import TestCase

@pytest.mark.django_db
@pytest.mark.models
class TestDiscoveryModels:
    """Test cases for Discovery models"""
    
    def test_discovery_module_has_no_models(self):
        """Test that discovery module currently has no Django models"""
        from django.apps import apps
        from discovery import models
        
        # Discovery module should not have any Django models currently
        # All data is stored in OpenSearch
        discovery_models = apps.get_app_config('discovery').get_models()
        assert len(list(discovery_models)) == 0
