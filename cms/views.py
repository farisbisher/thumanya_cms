from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Program, Category
from .serializers import ProgramSerializer, CategorySerializer

# Create your views here.

def index(request):
    return HttpResponse("CMS Module - Welcome to the Content Management System")

class IsAdminOrEditor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["admin", "editor"]

class ProgramViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing programs.
    
    Provides CRUD operations for programs including:
    - List all programs
    - Create new program
    - Retrieve specific program
    - Update program
    - Delete program
    - Search programs by category
    """
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get programs filtered by category.
        
        Query Parameters:
        - category: Category name to filter by
        """
        category = request.query_params.get('category')
        if category:
            programs = self.queryset.filter(category__name=category)
        else:
            programs = self.queryset
        serializer = self.get_serializer(programs, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing categories.
    
    Provides CRUD operations for program categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

