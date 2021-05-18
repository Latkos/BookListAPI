from rest_framework.urlpatterns import format_suffix_patterns
from tasks import views
from django.urls import path

urlpatterns = [
    path('books/', views.BookList.as_view())
]
urlpatterns = format_suffix_patterns(urlpatterns)
