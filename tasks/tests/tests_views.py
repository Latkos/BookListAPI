import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from tasks.models import Account, Book, Operation, Purchase


class TestsViews:

    @pytest.mark.django_db
    def test_API_root(self):
        client = APIClient()
        response = client.get('')
        amount_of_hyperlinks = 3
        assert (response.status_code == 200)  # meaning we got to the API
        assert (len(response.data) == amount_of_hyperlinks)  # there are 3 hyperlinks -accounts, books and books-buy
        assert (list(response.data.keys()) == (['accounts', 'books', 'books-buy']))  # those are the hyperlink names

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

    @pytest.mark.django_db
    def test_account_list_displaying(self):
        user = User.objects.create_user(
            username='test',
            password='testpass',
        )
        Account.objects.create(balance=100.00, owner=user)
        client = APIClient()
        response = client.get('/accounts/')
        assert response.status_code == 200  # assert the API accepted our request
        data = response.data  # all the data in the response
        assert (data['count'] == 1)  # assert there's only one account
        results = self.get_results_dict(data)
        assert (results['account_id'] == 1)
        assert (results['owner'] == 1)
        assert (Decimal(results['balance']) == 100.00)
        # we asserted that the account we created is displayed correctly

    @staticmethod
    def get_results_dict(data):
        results = data['results']
        results = results[0]
        results = dict(results)
        return results

    @pytest.mark.django_db
    def test_account_creation_if_not_authenticated(self):
        user = User.objects.create_user(
            username='test',
            password='testpass',
        )
        client = APIClient()
        response = client.post('/accounts/', {"owner": user, "balance": 100.00})
        assert (response.status_code == 403)
        assert (response.data[
                    'detail'].code == 'not_authenticated')  # assert the server did inform user he's not logged
        assert (Account.objects.all().count() == 0)  # assert the account was not created

    @pytest.mark.django_db
    def test_account_creation_if_authenticated(self):
        User.objects.create_user(
            username='test',
            password='testpass',
        )
        client = APIClient()
        client.login(username='test',
                     password='testpass')  # we log with the same credentials we used while creating user
        response = client.post('/accounts/', {"owner": 1, "balance": 100.00})
        assert (response.status_code == 201)
        data = response.data
        assert (data['account_id'] == 1)
        assert (data['owner'] == 1)
        assert (Decimal(data['balance']) == 100)
        # if all the credentials are good, let's just see if an account was created
        assert (Account.objects.all().count() == 1)

    @pytest.mark.django_db
    def test_account_modification_owner_permission(self):
        User.objects.create_user(
            username='test',
            password='testpass',
        )
        User.objects.create_user(
            username='test2',
            password='testpass2',
        )
        client = APIClient()
        client.login(username='test', password='testpass')
        client.post('/accounts/', {"owner": 1, "balance": 100.00})
        # we have created an account as user 1. Let's try to modify it now
        client.logout()
        client.login(username='test2', password='testpass2')
        response = client.post('/accounts/', {"owner": 1, "balance": 200.00})
        assert (response.status_code == 400)  # user test2 cannot modify a balance account linked to user test1, so we
        assert (str(response.data['owner'][0]) == 'This field must be unique.')
        # we need to assure that the code always rejects such post due to right reasons

    @pytest.mark.django_db
    def books_buy_endpoint_helper_startup(self, balance=100.00):
        Book.objects.create(title='book1', price=10.00)
        Book.objects.create(title='book2', price=30.00)
        user = User.objects.create_user(
            username='test',
            password='testpass',
        )
        Account.objects.create(balance=balance, owner=user)
        return user

    @pytest.mark.django_db
    def test_books_buy_endpoint_purchase_not_authenticated(self):
        self.books_buy_endpoint_helper_startup()
        client = APIClient()
        response = client.post('/books/buy/', {"books": [1, 2]})
        assert (response.status_code == 403)  # user is not logged in, so it should return 403
        assert (str(response.data['detail']) == 'Authentication credentials were not provided.')
        # again we assure that the server informs the user with a standard message

    @pytest.mark.django_db
    def test_books_buy_endpoint_successful_purchase(self):
        user = self.books_buy_endpoint_helper_startup()
        client = APIClient()
        client.login(username='test', password='testpass')
        data = {"books": [1, 2]}
        response = client.post('/books/buy/', data, format='json')
        data = response.data
        assert (data[0] == [1, 2])
        assert (data[1] == Decimal('40'))
        account = Account.objects.get(owner=user)
        assert (account.balance == 60.00)  # assert the price was deducted from the account

    @pytest.mark.django_db
    def test_books_buy_endpoint_insufficient_funds(self):
        user = self.books_buy_endpoint_helper_startup(balance=5.00)
        client = APIClient()
        client.login(username='test', password='testpass')
        data = {"books": [1, 2]}
        response = client.post('/books/buy/', data, format='json')
        assert (response.status_code == 400)  # assert that server rejected the transaction
        assert (response.data == 'Cannot perform such operation, since the funds are insufficient')
        account = Account.objects.get(owner=user)  # get the account from database in case of any change
        assert (account.balance == 5.00)  # assert the balance has not changed
        assert (Purchase.objects.all().count() == 0)
        assert (Operation.objects.all().count() == 0)
        # assert no purchase or operation remains in the database after an unsuccessful transaction attempt

    @pytest.mark.django_db
    def test_books_buy_endpoint_non_existing_book_id(self):
        self.books_buy_endpoint_helper_startup()
        client = APIClient()
        client.login(username='test', password='testpass')
        data = {"books": [1, 3]}
        response = client.post('/books/buy/', data, format='json')
        assert (response.status_code == 400)  # assert that server rejected the transaction
        data = response.data
        assert (data['books'][0] == 'Invalid pk "3" - object does not exist.')
        # this is also a standard framework message, so we assert it is returned
