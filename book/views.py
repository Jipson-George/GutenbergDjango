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
        books = BooksBook.objects.all()

        # Filter by Gutenberg IDs
        ids = request.GET.get('ids')
        if ids:
            id_list = [int(i) for i in ids.split(',')]
            books = books.filter(gutenberg_id__in=id_list)

        # Filter by language
        languages = request.GET.get('language')
        if languages:
            lang_list = languages.split(',')
            books = books.filter(booksbooklanguages__language__code__in=lang_list)

        # Filter by mime-type
        mimes = request.GET.get('mime_type')
        if mimes:
            mime_list = mimes.split(',')
            books = books.filter(booksformat__mime_type__in=mime_list)

        # Filter by topic (subject or bookshelf)
        topic = request.GET.get('topic')
        if topic:
            topic_list = topic.lower().split(',')
            books = books.filter(
                Q(booksbooksubjects__subject__name__icontains=topic_list[0]) |
                Q(booksbookbookshelves__bookshelf__name__icontains=topic_list[0])
            )
            for t in topic_list[1:]:
                books = books.filter(
                    Q(booksbooksubjects__subject__name__icontains=t) |
                    Q(booksbookbookshelves__bookshelf__name__icontains=t)
                )

        # Filter by author
        author = request.GET.get('author')
        if author:
            books = books.filter(booksbookauthors__author__name__icontains=author)

        # Filter by title
        title = request.GET.get('title')
        if title:
            books = books.filter(title__icontains=title)

        # Order by popularity (downloads)
        books = books.order_by('-download_count').distinct()

        # Pagination (25 per page)
        paginator = PageNumberPagination()
        paginator.page_size = 25
        paginated_books = paginator.paginate_queryset(books, request)

        serializer = BookSerializer(paginated_books, many=True)
        return paginator.get_paginated_response({
            'total_books': books.count(),
            'results': serializer.data
        })
