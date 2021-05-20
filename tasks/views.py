from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from tasks.models import Book, Account
from tasks.permissions import IsOwnerOrReadOnly
from tasks.serializers import BookSerializer, AccountSerializer, PurchaseSerializer


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
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class AccountList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated,
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
            book_id = int(book)
            book_object = Book.objects.get(book_id=book_id)
            model_object.books.add(book_object)
        try:
            model_object.save()  # to reflect the changes, we need to save the object
        except ValueError as exception:
            return Response(str(exception), status=status.HTTP_400_BAD_REQUEST)
        # it won't create a new operation again, just change the current operation's balance
        total_price = -1 * model_object.operation.balance_change # price should be positive, balance change is negative
        returned_data = []
        returned_data.append(books)
        returned_data.append(total_price)
        return Response(returned_data, status=status.HTTP_201_CREATED)

    def get(self, request, format=None):
        message = 'Please input books in format: {"books": [a,b,...]"}, where a,b,... are the IDs of books to purhcase'
        return Response(message,status.HTTP_204_NO_CONTENT)
