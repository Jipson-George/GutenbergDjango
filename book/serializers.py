# serializers.py
from rest_framework import serializers
from .models import BooksBook, BooksAuthor, BooksBookshelf, BooksSubject, BooksFormat, BooksBookAuthors, BooksBookSubjects, BooksBookBookshelves, BooksBookLanguages, BooksLanguage

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BooksAuthor
        fields = ['name', 'birth_year', 'death_year']

class BookshelfSerializer(serializers.ModelSerializer):
    class Meta:
        model = BooksBookshelf
        fields = ['name']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = BooksSubject
        fields = ['name']

class FormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = BooksFormat
        fields = ['mime_type', 'url']

class BookSerializer(serializers.ModelSerializer):
    authors = serializers.SerializerMethodField()
    subjects = serializers.SerializerMethodField()
    bookshelves = serializers.SerializerMethodField()
    formats = FormatSerializer(source='booksformat_set', many=True)
    language = serializers.SerializerMethodField()
    download_count = serializers.IntegerField()

    class Meta:
        model = BooksBook
        fields = ['download_count', 'gutenberg_id', 'title', 'authors', 'language', 'bookshelves', 'subjects', 'formats']

    def get_authors(self, obj):
        authors = BooksAuthor.objects.filter(booksbookauthors__book=obj)
        return AuthorSerializer(authors, many=True).data

    def get_subjects(self, obj):
        subjects = BooksSubject.objects.filter(booksbooksubjects__book=obj)
        return SubjectSerializer(subjects, many=True).data

    def get_bookshelves(self, obj):
        shelves = BooksBookshelf.objects.filter(booksbookbookshelves__book=obj)
        return BookshelfSerializer(shelves, many=True).data

    def get_language(self, obj):
        langs = BooksLanguage.objects.filter(booksbooklanguages__book=obj)
        return [l.code for l in langs]
