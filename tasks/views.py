from tasks.models import Book
from tasks.serializers import BookSerializer
from rest_framework import generics


class BookList(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
