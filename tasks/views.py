from rest_framework.views import APIView

from tasks.models import Book, Account, Purchase
from tasks.permissions import IsOwnerOrReadOnly
from tasks.serializers import BookSerializer, AccountSerializer, PurchaseSerializer
from rest_framework import generics, mixins, status
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

#
def create_books():
    Book.objects.create(title='Count of Monte Cristo', price=50.00)
    Book.objects.create(title='The Stranger', price=35.00)
    Book.objects.create(title='Dialogues', price=25.00)
    Book.objects.create(title='Les Miserables', price=70.00)
    Book.objects.create(title='Thinking Fast and Slow', price=60.00)


@api_view(['GET'])
def api_root(request, format=None):  # root of our API offers everything the API has to offer to a normal user
    # the login page is available in the upper right corner
    return Response({
        'accounts': reverse('accounts-list', request=request, format=format),
        'books': reverse('book-list', request=request, format=format),
        'books-buy': reverse('books-buy', request=request, format=format),
    })


# using ListAPIView from generics for both views because it simplifies view creation immensely
class BookList(generics.ListAPIView):
    # create_books()
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class AccountList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PurchaseCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        current_account = Account.objects.filter(owner=request.user).first()
        # we got the account associated with current user
        request.data.update({'account': current_account.pk})  # passing the account's primary field to data
        request.data.update({'operation': None})  # the operation is created in the model, so it needn't be passed
        serializer = PurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # if the data is invalid, it'll raise exception on the user's end
        model_object = serializer.save()  # save the model object for now
        books = request.data['books']
        for book in books:  # due to many-to-many relationship with books, we need to pass them later
            id = int(book)
            book_object = Book.objects.get(book_id=id)
            model_object.books.add(book_object)
        try:
            model_object.save()  # to reflect the changes, we need to save the object
        except ValueError as exception:
            return Response(str(exception), status=status.HTTP_400_BAD_REQUEST)
        # it won't create a new operation again, just change the current operation's balance
        total_price = -1 * model_object.operation.balance_change
        books.append(total_price)
        return Response(books, status=status.HTTP_201_CREATED)
