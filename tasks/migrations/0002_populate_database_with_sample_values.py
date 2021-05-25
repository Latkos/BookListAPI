from django.contrib.auth.models import User
from django.db import migrations

from tasks.models import Account, Book


def populate_with_sample_data(apps, schema_editor):
    user = User.objects.create_user(
        username='sample_user',
        password='book_pass',
    )
    Account.objects.create(balance=150.00, owner=user)
    Book.objects.create(title='Count of Monte Cristo', price=50.00)
    Book.objects.create(title='The Stranger', price=40.00)
    Book.objects.create(title='Dialogues', price=25.00)
    Book.objects.create(title='Les Miserables', price=70.00)
    Book.objects.create(title='Thinking Fast and Slow', price=60.00)


class Migration(migrations.Migration):
    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_with_sample_data)
    ]
