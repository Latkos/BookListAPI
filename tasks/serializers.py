from rest_framework import serializers

from tasks.models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model=Book
        fields=['book_id','title','price']