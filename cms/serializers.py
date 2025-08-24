from rest_framework import serializers
from .models import Program, Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    
    Fields:
    - id: Unique identifier
    - name: Category name
    - description: Category description
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class ProgramSerializer(serializers.ModelSerializer):
    """
    Serializer for Program model.
    
    Fields:
    - id: Unique identifier
    - title: Program title
    - description: Program description
    - category: Associated category
    - language: Program language
    - duration: Program duration
    - publish_date: Publication date
    - media_type: Type of media
    - media_url: URL to media content
    - thumbnail_url: URL to thumbnail image
    - metadata: Additional metadata (JSON)
    - created_at: Creation timestamp
    - updated_at: Last update timestamp
    """
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Program
        fields = [
            'id', 'title', 'description', 'category', 'category_id', 'language',
            'duration', 'publish_date', 'media_type', 'media_url',
            'thumbnail_url', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
