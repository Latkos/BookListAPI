from tasks.models import Book, Account
from tasks.permissions import IsOwnerOrReadOnly
from tasks.serializers import BookSerializer, AccountSerializer
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])

def api_root(request, format=None): #root of our API offers everything the API has to offer for a normal user
    return Response({
        'accounts': reverse('accounts-list', request=request, format=format),
        'books': reverse('book-list', request=request, format=format)
    })

# using ListAPIView from generics because it simplifies view creation immensely


class BookList(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class AccountList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
