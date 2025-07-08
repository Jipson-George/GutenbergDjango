from django.shortcuts import render

# Create your views here.
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import BooksBook
from .serializers import BookSerializer

class BookListView(APIView):
    def get(self, request):
        # Filter out books with no gutenberg_id or download_count
        books = BooksBook.objects.filter(
            gutenberg_id__isnull=False,
            download_count__isnull=False,
            download_count__gt=0  # Also exclude books with 0 downloads
        ).exclude(gutenberg_id='')

        # Filter by Gutenberg IDs
        ids = request.GET.get('ids')
        if ids:
            id_list = [int(i.strip()) for i in ids.split(',')]
            books = books.filter(gutenberg_id__in=id_list)

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
            topic_list = [t.strip().lower() for t in topic.split(',')]
            topic_q = Q()
            for t in topic_list:
                topic_q |= (Q(booksbooksubjects__subject__name__icontains=t) |
                           Q(booksbookbookshelves__bookshelf__name__icontains=t))
            books = books.filter(topic_q)

        # Filter by author - support multiple authors
        author = request.GET.get('author')
        if author:
            author_list = [a.strip() for a in author.split(',')]
            author_q = Q()
            for a in author_list:
                author_q |= Q(booksbookauthors__author__name__icontains=a)
            books = books.filter(author_q)

        # Filter by title - support multiple titles
        title = request.GET.get('title')
        if title:
            title_list = [t.strip() for t in title.split(',')]
            title_q = Q()
            for t in title_list:
                title_q |= Q(title__icontains=t)
            books = books.filter(title_q)

        # Filter out NULL download_count before ordering
        books = books.filter(download_count__isnull=False)
        
        # Order by popularity (downloads) and make distinct
        books = books.order_by('-download_count').distinct()
        
        # Get total count before pagination
        total_count = books.count()

        # Pagination (25 per page)
        paginator = PageNumberPagination()
        paginator.page_size = 25
        paginated_books = paginator.paginate_queryset(books, request)

        serializer = BookSerializer(paginated_books, many=True)
        
        # Custom response format to ensure proper structure
        response_data = {
            'count': total_count,
            'results': serializer.data
        }
        
        return paginator.get_paginated_response(response_data)