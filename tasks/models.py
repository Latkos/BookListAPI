from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from djchoices import ChoiceItem, DjangoChoices


class Account(models.Model):
    """
    Account model holds current balance of every user.
    """
    owner = models.OneToOneField(User, related_name='accounts', on_delete=models.CASCADE)
    balance = models.DecimalField(decimal_places=2, max_digits=20)  # arbitrary maximum digits amount

    # the type used for price is DecimalField because it's better for representing currency

    def deposit(self, amount):
        if amount < 0:
            raise ValueError("The deposited amount should not be negative, that's what purchases are for!")
        return Operation.objects.create(account=self, balance_change=amount, operation_type='deposition')


class Operation(models.Model):
    """
    Each change (deposit, purchase, etc..) of Account's balance should be reflected
    in the Operation model for auditing purposes.
    """

    class OperationTypes(DjangoChoices):
        deposition = ChoiceItem()
        deduction = ChoiceItem()

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    balance_change = models.DecimalField(decimal_places=2,
                                         max_digits=20)  # positive for deposit, negative for purchase
    operation_type = models.CharField(max_length=20, choices=OperationTypes.choices, default='deduction')
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # call the "real" save() method
        new_balance = self.account.balance + self.balance_change
        if new_balance > 0:
            self.account.balance = new_balance
            self.account.save()
        # this part should not be reached, because purchase already handles such cases
        # however implementing some protection in case of manual Operation modification
        else:
            self.delete()
            raise Exception("The operation would leave the balance negative. "
                            "Operations should not be tampered with manually")


class Book(models.Model):
    """
    Model stores a title of the book and its price.
    """
    title = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(Decimal('0.01'))])


class Purchase(models.Model):
    """
    Model stores data about purchases.
    """
    books = models.ManyToManyField(Book)  # again, if we're bound to 4 of those models, there needs to be a many-to-many
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, null=True)

    @classmethod
    def is_transaction_possible(cls, account_balance, transaction_price):
        return account_balance - transaction_price >= 0

    @classmethod
    def collect_books_and_return_purchase_cost(cls, books_id_list):
        books = []
        purchase_cost = 0
        for book in books_id_list:  # due to many-to-many relationship with books, we need to pass them later
            book_id = int(book)
            book_object = Book.objects.get(id=book_id)
            books.append(book_object)
            purchase_cost += book_object.price
        return books, purchase_cost
