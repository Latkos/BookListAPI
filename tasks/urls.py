from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path, include
from tasks import views

urlpatterns = format_suffix_patterns([
    path('', views.api_root),
    path('books/', views.BookList.as_view(), name='book-list'),
    path('accounts/', views.AccountList.as_view(), name='accounts-list'),
    path('login/', include('rest_framework.urls')),
    path('books/buy/', views.PurchaseCreate.as_view(), name='books-buy'),
])
