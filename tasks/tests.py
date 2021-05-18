# DISCLAIMER: since the tests are generally built to verify business logic, I did not test functions from
# Django, Python, REST API etc., since they are presumed to work correctly
# Thus I mostly tested self-made methods (or the ones I did actually change a bit)
# *****************************************************************************************************************

from django.contrib.auth.models import User

import pytest
from tasks.models import Account, Book, Operation, Purchase
from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient


class TestModels:

    @pytest.mark.django_db
    # simple setup function in order to not repeat myself, creates 1 Django auth.User, 1 corresponding account and 2 books
    def set_up(self, account_balance):
        user = User.objects.create_user(
            username='test',
            password='testpass',
        )
        Account.objects.create(balance=account_balance, owner=user)
        Book.objects.create(title='book1', price=10.00)
        Book.objects.create(title='book2', price=20.00)

    @pytest.mark.django_db
    def test_operation_creation_after_new_purchase(self):
        self.set_up(100.00)
        book1 = Book.objects.get(book_id=1)
        book2 = Book.objects.get(book_id=2)
        collective_price = book1.price + book2.price
        purchase = Purchase.objects.create(account_id=1)  # we create a purchase transaction
        purchase.books.add(book1)
        purchase.books.add(book2)
        purchase.save()
        assert (purchase.operation.balance_change == -collective_price)
        # the success of the assert above indicates that the purchase was created, with books and operations added correctly
        # and that the operation balance was calculated correctly

    @pytest.mark.django_db
    def test_purchase_behavior_if_funds_insufficient(self):
        self.set_up(5.00)
        book1 = Book.objects.get(book_id=1)
        with pytest.raises(ValueError):
            purchase = Purchase.objects.create(account_id=1)
            purchase.books.add(book1)
            purchase.save()

    @pytest.mark.django_db
    def test_account_balance_change_after_operation_creation(self):
        self.set_up(100.00)
        account1 = Account.objects.get(account_id=1)
        assert (account1.balance == 100)
        operation = Operation.objects.create(account=account1, balance_change=-30)
        assert (account1.balance == 100 + operation.balance_change)

    @pytest.mark.django_db
    def test_deposit(self):
        self.set_up(100)
        account = Account.objects.get(account_id=1)
        account.deposit(100)
        assert (account.balance == 200)

    @pytest.mark.django_db
    def test_negative_value_for_deposit(self):
        self.set_up(100)
        account = Account.objects.get(account_id=1)
        with pytest.raises(ValueError):
            account.deposit(-100)


class TestViews:

    @pytest.mark.django_db
    def test_API_root(self):
        client = APIClient()
        response = client.get('')
        amount_of_hyperlinks = 3
        assert (response.status_code == 200)  # meaning we got to the API
        assert (len(response.data) == amount_of_hyperlinks)  # there are 3 hyperlinks -accounts, books and books-buy
        assert (list(response.data.keys()) == (['accounts', 'books', 'books-buy'])) # those are the hyperlink names

    @pytest.mark.django_db
    def test_books_endpoint_without_any_books(self):
        client = APIClient()
        response = client.get('/books/')
        data = response.data
        assert (data['count'] == 0)
        assert (len(data['results']) == 0)

    @pytest.mark.django_db
    def test_books_endpoint_with_sample_books(self):
        Book.objects.create(title='book1', price=10.00)
        Book.objects.create(title='book2', price=30.00)
        client = APIClient()
        response = client.get('/books/')
        data = response.data
        assert (data['count'] == 2)
        assert (len(data['results']) == 2)
