from rest_framework import serializers
from django.contrib.auth.models import User
from tasks.models import Book, Account, Purchase


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['book_id', 'title', 'price']


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['account_id', 'owner', 'balance']


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        optional_fields = ['operation']
        fields = ('purchase_id', 'books', 'account')