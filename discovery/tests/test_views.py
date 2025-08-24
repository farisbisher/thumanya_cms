"""
Unit tests for Discovery module views
"""
import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
@pytest.mark.views
@pytest.mark.api
class TestDiscoveryViews:
    """Test cases for Discovery views"""
    
    @patch('discovery.views.OpenSearch')
    def test_search_view_missing_query_parameter(self, mock_opensearch, api_client):
        """Test search view with missing query parameter"""
        response = api_client.get(reverse('discovery:search'))
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert 'Query parameter' in response.data['error']
    
    @patch('discovery.views.OpenSearch')
    def test_search_view_empty_query_parameter(self, mock_opensearch, api_client):
        """Test search view with empty query parameter"""
        response = api_client.get(reverse('discovery:search'), {'q': ''})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert 'Query parameter' in response.data['error']
    
    @patch('discovery.views.OpenSearch')
    def test_search_view_basic_search(self, mock_opensearch, api_client):
        """Test search view with basic search query"""
        # Mock OpenSearch client
        mock_client = MagicMock()
        mock_opensearch.return_value = mock_client
        
        # Mock search response
        mock_response = {
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
        
        mock_client.search.return_value = mock_response
        
        response = api_client.get(reverse('discovery:search'), {'q': 'test'})
        
        assert response.status_code == status.HTTP_200_OK
        assert 'query' in response.data
        assert 'total' in response.data
        assert 'results' in response.data
        assert 'took' in response.data
        assert 'aggregations' in response.data
        
        assert response.data['query'] == 'test'
        assert response.data['total'] == 1
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Test Program'
        assert response.data['results'][0]['score'] == 0.95
    
    @patch('discovery.views.OpenSearch')
    def test_search_view_with_filters(self, mock_opensearch, api_client):
        """Test search view with various filters"""
        # Mock OpenSearch client
        mock_client = MagicMock()
        mock_opensearch.return_value = mock_client
        
        # Mock search response
        mock_response = {
            'hits': {
                'total': {'value': 0},
                'hits': []
            },
            'took': 2,
            'aggregations': {}
        }
        
        mock_client.search.return_value = mock_response
        
        # Test with category filter
        response = api_client.get(reverse('discovery:search'), {
            'q': 'test',
            'category': 'Technology'
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        # Test with language filter
        response = api_client.get(reverse('discovery:search'), {
            'q': 'test',
            'language': 'English'
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        # Test with media_type filter
        response = api_client.get(reverse('discovery:search'), {
            'q': 'test',
            'media_type': 'video'
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        # Test with multiple filters
        response = api_client.get(reverse('discovery:search'), {
            'q': 'test',
            'category': 'Technology',
            'language': 'English',
            'media_type': 'video',
            'duration_min': '0:30:00',
            'duration_max': '1:00:00',
            'publish_date_from': '2024-01-01',
            'publish_date_to': '2024-12-31',
            'tags': 'test,technology',
            'sort_by': 'publish_date',
            'sort_order': 'desc',
            'page': '2',
            'page_size': '10',
            'highlight': 'true',
            'fuzzy': 'true'
        })
        
        assert response.status_code == status.HTTP_200_OK
    
    @patch('discovery.views.OpenSearch')
    def test_search_view_opensearch_error(self, mock_opensearch, api_client):
        """Test search view when OpenSearch returns an error"""
        # Mock OpenSearch client to raise an exception
        mock_client = MagicMock()
        mock_opensearch.return_value = mock_client
        mock_client.search.side_effect = Exception("OpenSearch connection error")
        
        response = api_client.get(reverse('discovery:search'), {'q': 'test'})
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data
        assert 'Search failed' in response.data['error']
    
    @patch('discovery.views.OpenSearch')
    def test_search_view_pagination(self, mock_opensearch, api_client):
        """Test search view pagination"""
        # Mock OpenSearch client
        mock_client = MagicMock()
        mock_opensearch.return_value = mock_client
        
        # Mock search response with pagination
        mock_response = {
            'hits': {
                'total': {'value': 25},
                'hits': []
            },
            'took': 5,
            'aggregations': {}
        }
        
        mock_client.search.return_value = mock_response
        
        # Test first page
        response = api_client.get(reverse('discovery:search'), {
            'q': 'test',
            'page': '1',
            'page_size': '10'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['page'] == 1
        assert response.data['page_size'] == 10
        assert response.data['total_pages'] == 3  # 25 items / 10 per page = 3 pages
        
        # Test second page
        response = api_client.get(reverse('discovery:search'), {
            'q': 'test',
            'page': '2',
            'page_size': '10'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['page'] == 2
    
    @patch('discovery.views.OpenSearch')
    def test_search_view_sorting(self, mock_opensearch, api_client):
        """Test search view sorting options"""
        # Mock OpenSearch client
        mock_client = MagicMock()
        mock_opensearch.return_value = mock_client
        
        mock_response = {
            'hits': {
                'total': {'value': 0},
                'hits': []
            },
            'took': 2,
            'aggregations': {}
        }
        
        mock_client.search.return_value = mock_response
        
        # Test different sort options
        sort_options = ['_score', 'title', 'publish_date', 'created_at']
        
        for sort_by in sort_options:
            response = api_client.get(reverse('discovery:search'), {
                'q': 'test',
                'sort_by': sort_by,
                'sort_order': 'desc'
            })
            
            assert response.status_code == status.HTTP_200_OK
    
    def test_index_view(self, api_client):
        """Test discovery index view"""
        response = api_client.get(reverse('discovery:index'))
        
        assert response.status_code == status.HTTP_200_OK
        assert 'Discovery Module' in response.content.decode()

@pytest.mark.django_db
@pytest.mark.integration
class TestDiscoveryIntegration:
    """Integration test cases for Discovery module"""
    
    @patch('discovery.views.OpenSearch')
    def test_complete_search_workflow(self, mock_opensearch, api_client):
        """Test complete search workflow with various parameters"""
        # Mock OpenSearch client
        mock_client = MagicMock()
        mock_opensearch.return_value = mock_client
        
        # Mock search response
        mock_response = {
            'hits': {
                'total': {'value': 5},
                'hits': [
                    {
                        '_source': {
                            'id': i,
                            'title': f'Program {i}',
                            'description': f'Description {i}',
                            'category': 'Technology',
                            'language': 'English',
                            'duration': '0:30:00',
                            'publish_date': '2024-01-01',
                            'media_type': 'video',
                            'media_url': f'https://example.com/video{i}',
                            'thumbnail_url': f'https://example.com/thumb{i}.jpg',
                            'metadata': {'tags': ['test', 'technology']},
                            'created_at': '2024-01-01T00:00:00Z',
                            'updated_at': '2024-01-01T00:00:00Z'
                        },
                        '_score': 0.9 - (i * 0.1),
                        'highlight': {
                            'title': [f'<em>Program</em> {i}']
                        }
                    } for i in range(1, 6)
                ]
            },
            'took': 10,
            'aggregations': {
                'categories': {
                    'buckets': [
                        {'key': 'Technology', 'doc_count': 5}
                    ]
                },
                'languages': {
                    'buckets': [
                        {'key': 'English', 'doc_count': 5}
                    ]
                },
                'media_types': {
                    'buckets': [
                        {'key': 'video', 'doc_count': 5}
                    ]
                },
                'duration_ranges': {
                    'buckets': [
                        {'key': '30-60 min', 'doc_count': 5}
                    ]
                }
            }
        }
        
        mock_client.search.return_value = mock_response
        
        # Test comprehensive search
        response = api_client.get(reverse('discovery:search'), {
            'q': 'technology program',
            'category': 'Technology',
            'language': 'English',
            'media_type': 'video',
            'duration_min': '0:30:00',
            'duration_max': '1:00:00',
            'publish_date_from': '2024-01-01',
            'publish_date_to': '2024-12-31',
            'tags': 'test,technology',
            'sort_by': 'publish_date',
            'sort_order': 'desc',
            'page': '1',
            'page_size': '5',
            'highlight': 'true',
            'fuzzy': 'true'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['query'] == 'technology program'
        assert response.data['total'] == 5
        assert len(response.data['results']) == 5
        assert response.data['page'] == 1
        assert response.data['page_size'] == 5
        assert response.data['total_pages'] == 1
        assert 'aggregations' in response.data
        assert 'filters_applied' in response.data
        
        # Verify filters were applied
        filters = response.data['filters_applied']
        assert filters['category'] == 'Technology'
        assert filters['language'] == 'English'
        assert filters['media_type'] == 'video'
        assert filters['sort_by'] == 'publish_date'
        assert filters['sort_order'] == 'desc'
    
    @patch('discovery.views.OpenSearch')
    def test_search_with_aggregations(self, mock_opensearch, api_client):
        """Test search with aggregations for faceted search"""
        # Mock OpenSearch client
        mock_client = MagicMock()
        mock_opensearch.return_value = mock_client
        
        # Mock search response with rich aggregations
        mock_response = {
            'hits': {
                'total': {'value': 10},
                'hits': []
            },
            'took': 15,
            'aggregations': {
                'categories': {
                    'buckets': [
                        {'key': 'Technology', 'doc_count': 5},
                        {'key': 'Science', 'doc_count': 3},
                        {'key': 'History', 'doc_count': 2}
                    ]
                },
                'languages': {
                    'buckets': [
                        {'key': 'English', 'doc_count': 7},
                        {'key': 'Arabic', 'doc_count': 3}
                    ]
                },
                'media_types': {
                    'buckets': [
                        {'key': 'video', 'doc_count': 6},
                        {'key': 'audio', 'doc_count': 4}
                    ]
                },
                'duration_ranges': {
                    'buckets': [
                        {'key': '0-30 min', 'doc_count': 3},
                        {'key': '30-60 min', 'doc_count': 4},
                        {'key': '1-2 hours', 'doc_count': 2},
                        {'key': '2+ hours', 'doc_count': 1}
                    ]
                }
            }
        }
        
        mock_client.search.return_value = mock_response
        
        response = api_client.get(reverse('discovery:search'), {'q': 'test'})
        
        assert response.status_code == status.HTTP_200_OK
        assert 'aggregations' in response.data
        
        aggregations = response.data['aggregations']
        assert 'categories' in aggregations
        assert 'languages' in aggregations
        assert 'media_types' in aggregations
        assert 'duration_ranges' in aggregations
        
        # Verify aggregation data
        categories = aggregations['categories']['buckets']
        assert len(categories) == 3
        assert categories[0]['key'] == 'Technology'
        assert categories[0]['doc_count'] == 5 