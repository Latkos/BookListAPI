from rest_framework import serializers
from tasks.models import Book, Account, Purchase


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'price']


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'owner', 'balance']


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        optional_fields = ['operation']
        fields = ('id', 'books', 'account')
