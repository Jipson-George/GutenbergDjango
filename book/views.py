from django.shortcuts import render

# Create your views here.
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import BooksBook, BooksBookAuthors, BooksBookBookshelves, BooksBookLanguages, BooksBookSubjects, BooksFormat
from .serializers import BookSerializer

from django.db.models import Q, Prefetch
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class BookListView(APIView):
    def get(self, request):
        # Start with base queryset with essential filters
        books = BooksBook.objects.filter(
            gutenberg_id__isnull=False,
            download_count__isnull=False,
            download_count__gt=0
        ).exclude(gutenberg_id='')
        
        # Apply filters efficiently
        books = self._apply_filters(books, request)
        
        # Use select_related and prefetch_related for optimization
        books = books.select_related().prefetch_related(
            Prefetch('booksbookauthors_set', 
                    queryset=BooksBookAuthors.objects.select_related('author')),
            Prefetch('booksbooksubjects_set',
                    queryset=BooksBookSubjects.objects.select_related('subject')),
            Prefetch('booksbookbookshelves_set',
                    queryset=BooksBookBookshelves.objects.select_related('bookshelf')),
            Prefetch('booksbooklanguages_set',
                    queryset=BooksBookLanguages.objects.select_related('language')),
            Prefetch('booksformat_set',
                    queryset=BooksFormat.objects.only('mime_type', 'url', 'book_id'))
        )
        
        # Order by popularity and make distinct
        books = books.order_by('-download_count').distinct()
        
        # Get total count before pagination (use exists() for better performance)
        total_count = books.count()
        
        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 25
        paginated_books = paginator.paginate_queryset(books, request)
        
        serializer = BookSerializer(paginated_books, many=True)
        
        response_data = {
            'count': total_count,
            'results': serializer.data
        }
        
        return paginator.get_paginated_response(response_data)
    
    def _apply_filters(self, books, request):
        """Apply all filters efficiently"""
        
        # Filter by Gutenberg IDs
        ids = request.GET.get('ids')
        if ids:
            try:
                id_list = [int(i.strip()) for i in ids.split(',')]
                books = books.filter(gutenberg_id__in=id_list)
            except ValueError:
                pass  # Skip invalid IDs
        
        # Filter by language
        languages = request.GET.get('language')
        if languages:
            lang_list = [lang.strip() for lang in languages.split(',')]
            books = books.filter(booksbooklanguages__language__code__in=lang_list)
        
        # Filter by mime-type
        mimes = request.GET.get('mime_type')
        if mimes:
            mime_list = [mime.strip() for mime in mimes.split(',')]
            books = books.filter(booksformat__mime_type__in=mime_list)
        
        # Filter by topic (subject or bookshelf) - OR logic for multiple topics
        topic = request.GET.get('topic')
        if topic:
            topic_list = [t.strip() for t in topic.split(',') if t.strip()]
            if topic_list:
                topic_q = Q()
                for t in topic_list:
                    topic_q |= (Q(booksbooksubjects__subject__name__icontains=t) |
                               Q(booksbookbookshelves__bookshelf__name__icontains=t))
                books = books.filter(topic_q)
        
        # Filter by author - support multiple authors
        author = request.GET.get('author')
        if author:
            author_list = [a.strip() for a in author.split(',') if a.strip()]
            if author_list:
                author_q = Q()
                for a in author_list:
                    author_q |= Q(booksbookauthors__author__name__icontains=a)
                books = books.filter(author_q)
        
        # Filter by title - support multiple titles
        title = request.GET.get('title')
        if title:
            title_list = [t.strip() for t in title.split(',') if t.strip()]
            if title_list:
                title_q = Q()
                for t in title_list:
                    title_q |= Q(title__icontains=t)
                books = books.filter(title_q)
        
        return books