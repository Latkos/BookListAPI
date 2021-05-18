# DISCLAIMER: since the tests are generally built to verify business logic, I did not test built-in Django functions,
# only custom methods (or the ones I overloaded) were tested

from decimal import Decimal

import pytest
from tasks.models import *


@pytest.mark.django_db
# simple setup function in order to not repeat myself
def set_up():
    Account.objects.create(user_name='user1', balance=100.00)
    Account.objects.create(user_name='user2', balance=200.00)
    Book.objects.create(title='book1', price=10.00)
    Book.objects.create(title='book2', price=20.00)


@pytest.mark.django_db
def test_operation_creation_after_account_creation():
    set_up()
    book1 = Book.objects.get(book_id=1)
    book2 = Book.objects.get(book_id=2)
    collective_price = book1.price + book2.price
    purchase1 = Purchase.objects.create(user_id=1)
    purchase1.books.add(book1)
    purchase1.books.add(book2)
    purchase1.save()
    assert (purchase1.operation.balance_change == -collective_price)
    # the success of the assert above indicates that the purchase was created, with books and operations added correctly


@pytest.mark.django_db
def test_account_balance_change_after_operation_creation():
    set_up()
    account1 = Account.objects.get(account_id=1)
    assert (account1.balance == 100)
    operation = Operation.objects.create(account=account1, balance_change=-30)
    assert (account1.balance == 100 + operation.balance_change)

# @pytest.mark.django_db
# def test_purchase_creation():