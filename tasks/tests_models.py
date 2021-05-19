# DISCLAIMER: since the tests are generally built to verify business logic, I did not test functions from
# Django, Python, REST API etc., since they are presumed to work correctly
# Thus I mostly tested self-made methods (or the ones I did actually change a bit)
# The code coverage for views.py and models.py as I'm writing this is 100% and 100%
# *****************************************************************************************************************

from decimal import Decimal

from django.contrib.auth.models import User

import pytest
from tasks.models import Account, Book, Operation, Purchase


class TestsModels:

    @pytest.mark.django_db
    # simple setup function in order to not repeat myself, creates 1 Django auth.User, 1 account and 2 books
    def set_up(self, account_balance=100.00):
        user = User.objects.create_user(
            username='test',
            password='testpass',
        )
        Account.objects.create(balance=account_balance, owner=user)
        Book.objects.create(title='book1', price=10.00)
        Book.objects.create(title='book2', price=20.00)

    @pytest.mark.django_db
    def test_operation_creation_after_new_purchase(self):
        self.set_up()
        book1 = Book.objects.get(book_id=1)
        book2 = Book.objects.get(book_id=2)
        collective_price = book1.price + book2.price
        purchase = Purchase.objects.create(account_id=1)  # we create a purchase transaction
        purchase.books.add(book1)
        purchase.books.add(book2)
        purchase.save()
        assert (purchase.operation.balance_change == -collective_price)
        # the success of the assert above indicates that the purchase was created, books and operations were added
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
        self.set_up()
        account1 = Account.objects.get(account_id=1)
        assert (account1.balance == 100)
        operation = Operation.objects.create(account=account1, balance_change=-30)
        assert (account1.balance == 100 + operation.balance_change)

    @pytest.mark.django_db
    def test_deposit(self):
        self.set_up()
        account = Account.objects.get(account_id=1)
        account.deposit(100)
        assert (account.balance == 200)

    @pytest.mark.django_db
    def test_negative_value_deposit(self):
        self.set_up()
        account = Account.objects.get(account_id=1)
        with pytest.raises(ValueError):
            account.deposit(-100)

    @pytest.mark.django_db
    def test_negative_value_operation(self):
        self.set_up(5.00)
        account = Account.objects.get(account_id=1)
        with pytest.raises(Exception):
            Operation.objects.create(account=account,balance_change=Decimal(-100.00))



