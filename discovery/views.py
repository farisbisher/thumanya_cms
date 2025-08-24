from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from opensearchpy import OpenSearch, RequestsHttpConnection
import os
import logging

logger = logging.getLogger(__name__)

class SearchView(APIView):
    permission_classes = [AllowAny]
    
    def get_opensearch_client(self):
        """Get OpenSearch client"""
        opensearch_host = os.getenv("OPENSEARCH_HOST", "opensearch:9200")
        host, port = opensearch_host.split(":")
        
        client = OpenSearch(
            hosts=[{"host": host, "port": int(port)}],
            use_ssl=False,
            verify_certs=False,
            connection_class=RequestsHttpConnection,
            timeout=30
        )
        return client
    
    @extend_schema(
        operation_id="search_programs",
        summary="Search programs in OpenSearch",
        description="""
        Advanced search API for programs with multiple filtering and sorting options.
        
        This endpoint provides powerful search capabilities including:
        - Full-text search across multiple fields
        - Category and language filtering
        - Date range filtering
        - Duration filtering
        - Media type filtering
        - Advanced sorting options
        - Pagination support
        - Highlighting of search terms
        """,
        parameters=[
            OpenApiParameter(
                name="q",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Search query string (required)",
                required=True,
                examples=[
                    OpenApiExample(
                        "Simple search",
                        value="coffee",
                        description="Search for programs containing 'coffee'"
                    ),
                    OpenApiExample(
                        "Multi-word search",
                        value="arabic documentary",
                        description="Search for programs containing both 'arabic' and 'documentary'"
                    )
                ]
            ),
            OpenApiParameter(
                name="category",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter by category name",
                examples=[
                    OpenApiExample("Technology", value="Technology"),
                    OpenApiExample("Science", value="Science"),
                    OpenApiExample("History", value="History")
                ]
            ),
            OpenApiParameter(
                name="language",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter by language",
                examples=[
                    OpenApiExample("Arabic", value="Arabic"),
                    OpenApiExample("English", value="English"),
                    OpenApiExample("Spanish", value="Spanish")
                ]
            ),
            OpenApiParameter(
                name="media_type",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter by media type",
                examples=[
                    OpenApiExample("Documentary", value="documentary"),
                    OpenApiExample("Video", value="video"),
                    OpenApiExample("Audio", value="audio")
                ]
            ),
            OpenApiParameter(
                name="duration_min",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Minimum duration (format: HH:MM:SS or MM:SS)",
                examples=[
                    OpenApiExample("30 minutes", value="0:30:00"),
                    OpenApiExample("1 hour", value="1:00:00")
                ]
            ),
            OpenApiParameter(
                name="duration_max",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Maximum duration (format: HH:MM:SS or MM:SS)",
                examples=[
                    OpenApiExample("2 hours", value="2:00:00"),
                    OpenApiExample("45 minutes", value="0:45:00")
                ]
            ),
            OpenApiParameter(
                name="publish_date_from",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Publish date from (YYYY-MM-DD)",
                examples=[
                    OpenApiExample("2023-01-01", value="2023-01-01"),
                    OpenApiExample("2024-06-01", value="2024-06-01")
                ]
            ),
            OpenApiParameter(
                name="publish_date_to",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Publish date to (YYYY-MM-DD)",
                examples=[
                    OpenApiExample("2024-12-31", value="2024-12-31"),
                    OpenApiExample("2025-01-01", value="2025-01-01")
                ]
            ),
            OpenApiParameter(
                name="tags",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter by tags (comma-separated)",
                examples=[
                    OpenApiExample("Single tag", value="coffee"),
                    OpenApiExample("Multiple tags", value="coffee,history,yemen")
                ]
            ),
            OpenApiParameter(
                name="sort_by",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Sort field (default: _score)",
                examples=[
                    OpenApiExample("Relevance", value="_score"),
                    OpenApiExample("Title", value="title"),
                    OpenApiExample("Publish date", value="publish_date"),
                    OpenApiExample("Created date", value="created_at")
                ]
            ),
            OpenApiParameter(
                name="sort_order",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Sort order (asc/desc, default: desc)",
                examples=[
                    OpenApiExample("Descending", value="desc"),
                    OpenApiExample("Ascending", value="asc")
                ]
            ),
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Page number (default: 1)",
                examples=[
                    OpenApiExample("First page", value=1),
                    OpenApiExample("Second page", value=2)
                ]
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Results per page (default: 20, max: 100)",
                examples=[
                    OpenApiExample("Default", value=20),
                    OpenApiExample("Large page", value=50)
                ]
            ),
            OpenApiParameter(
                name="highlight",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="Enable highlighting (default: true)",
                examples=[
                    OpenApiExample("Enabled", value=True),
                    OpenApiExample("Disabled", value=False)
                ]
            ),
            OpenApiParameter(
                name="fuzzy",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="Enable fuzzy matching (default: true)",
                examples=[
                    OpenApiExample("Enabled", value=True),
                    OpenApiExample("Disabled", value=False)
                ]
            )
        ],
        responses={
            200: {
                "description": "Search results",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "total": {"type": "integer"},
                                "page": {"type": "integer"},
                                "page_size": {"type": "integer"},
                                "total_pages": {"type": "integer"},
                                "results": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "title": {"type": "string"},
                                            "description": {"type": "string"},
                                            "category": {"type": "string"},
                                            "language": {"type": "string"},
                                            "duration": {"type": "string"},
                                            "publish_date": {"type": "string"},
                                            "media_type": {"type": "string"},
                                            "media_url": {"type": "string"},
                                            "thumbnail_url": {"type": "string"},
                                            "metadata": {"type": "object"},
                                            "created_at": {"type": "string"},
                                            "updated_at": {"type": "string"},
                                            "score": {"type": "number"},
                                            "highlights": {"type": "object"}
                                        }
                                    }
                                },
                                "took": {"type": "integer"},
                                "aggregations": {"type": "object"}
                            }
                        }
                    }
                }
            },
            400: {"description": "Bad request - Invalid parameters"},
            500: {"description": "Internal server error"}
        },
        examples=[
            OpenApiExample(
                "Search for coffee programs",
                value={
                    "query": "coffee",
                    "total": 1,
                    "page": 1,
                    "page_size": 20,
                    "total_pages": 1,
                    "results": [
                        {
                            "id": 6,
                            "title": "2رحلة القهوة من اليمن إلى العالم",
                            "description": "وثائقي قصير من ثمانية عن تاريخ القهوة العربية.",
                            "category": "Technology",
                            "language": "Arabic",
                            "duration": "0:45:00",
                            "publish_date": "2023-10-12",
                            "media_type": "documentary",
                            "score": 1.0,
                            "highlights": {
                                "metadata.tags": ["<em>coffee</em>", "history", "Yemen"]
                            }
                        }
                    ],
                    "took": 5
                },
                response_only=True,
                status_codes=["200"]
            )
        ]
    )
    def get(self, request):
        """Advanced search programs in OpenSearch with comprehensive filtering"""
        query = request.GET.get('q', '')
        
        if not query:
            return Response({
                "error": "Query parameter 'q' is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            client = self.get_opensearch_client()
            
            # Parse parameters
            category = request.GET.get('category')
            language = request.GET.get('language')
            media_type = request.GET.get('media_type')
            duration_min = request.GET.get('duration_min')
            duration_max = request.GET.get('duration_max')
            publish_date_from = request.GET.get('publish_date_from')
            publish_date_to = request.GET.get('publish_date_to')
            tags = request.GET.get('tags')
            sort_by = request.GET.get('sort_by', '_score')
            sort_order = request.GET.get('sort_order', 'desc')
            page = int(request.GET.get('page', 1))
            page_size = min(int(request.GET.get('page_size', 20)), 100)
            highlight = request.GET.get('highlight', 'true').lower() == 'true'
            fuzzy = request.GET.get('fuzzy', 'true').lower() == 'true'
            
            # Calculate from/size for pagination
            from_size = (page - 1) * page_size
            
            # Build filter queries
            filter_queries = []
            
            if category:
                filter_queries.append({"term": {"category": category}})
            
            if language:
                filter_queries.append({"term": {"language": language}})
            
            if media_type:
                filter_queries.append({"term": {"media_type": media_type}})
            
            if duration_min or duration_max:
                duration_filter = {"range": {"duration": {}}}
                if duration_min:
                    duration_filter["range"]["duration"]["gte"] = duration_min
                if duration_max:
                    duration_filter["range"]["duration"]["lte"] = duration_max
                filter_queries.append(duration_filter)
            
            if publish_date_from or publish_date_to:
                date_filter = {"range": {"publish_date": {}}}
                if publish_date_from:
                    date_filter["range"]["publish_date"]["gte"] = publish_date_from
                if publish_date_to:
                    date_filter["range"]["publish_date"]["lte"] = publish_date_to
                filter_queries.append(date_filter)
            
            if tags:
                tag_list = [tag.strip() for tag in tags.split(',')]
                filter_queries.append({"terms": {"metadata.tags": tag_list}})
            
            # Build search query
            search_body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["title^3", "description^2", "metadata.tags^2", "category"],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO" if fuzzy else 0,
                                    "operator": "or"
                                }
                            }
                        ],
                        "filter": filter_queries
                    }
                },
                "from": from_size,
                "size": page_size,
                "sort": [
                    {sort_by: {"order": sort_order}},
                    {"created_at": {"order": "desc"}}
                ]
            }
            
            # Add highlighting if enabled
            if highlight:
                search_body["highlight"] = {
                    "fields": {
                        "title": {},
                        "description": {},
                        "metadata.tags": {}
                    },
                    "pre_tags": ["<em>"],
                    "post_tags": ["</em>"]
                }
            
            # Add aggregations for faceted search
            search_body["aggs"] = {
                "categories": {"terms": {"field": "category"}},
                "languages": {"terms": {"field": "language"}},
                "media_types": {"terms": {"field": "media_type"}},
                "duration_buckets": {
                    "terms": {
                        "field": "duration",
                        "size": 20
                    }
                }
            }
            
            # Execute search
            response = client.search(
                index="programs",
                body=search_body
            )
            
            # Process results
            hits = response.get('hits', {}).get('hits', [])
            total = response.get('hits', {}).get('total', {}).get('value', 0)
            total_pages = (total + page_size - 1) // page_size
            
            results = []
            for hit in hits:
                source = hit['_source']
                highlight = hit.get('highlight', {})
                
                result = {
                    "id": source.get('id'),
                    "title": source.get('title'),
                    "description": source.get('description'),
                    "category": source.get('category'),
                    "language": source.get('language'),
                    "duration": source.get('duration'),
                    "publish_date": source.get('publish_date'),
                    "media_type": source.get('media_type'),
                    "media_url": source.get('media_url'),
                    "thumbnail_url": source.get('thumbnail_url'),
                    "metadata": source.get('metadata'),
                    "created_at": source.get('created_at'),
                    "updated_at": source.get('updated_at'),
                    "score": hit.get('_score'),
                    "highlights": highlight
                }
                results.append(result)
            
            return Response({
                "query": query,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "results": results,
                "took": response.get('took', 0),
                "aggregations": response.get('aggregations', {}),
                "filters_applied": {
                    "category": category,
                    "language": language,
                    "media_type": media_type,
                    "duration_min": duration_min,
                    "duration_max": duration_max,
                    "publish_date_from": publish_date_from,
                    "publish_date_to": publish_date_to,
                    "tags": tags,
                    "sort_by": sort_by,
                    "sort_order": sort_order
                }
            })
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return Response({
                "error": "Search failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def index(request):
    return HttpResponse("Discovery Module - Advanced Search API is working!")
