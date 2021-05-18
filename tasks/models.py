from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User


class Account(models.Model):
    """
    Account model holds current balance of every user.
    """
    account_id = models.AutoField(primary_key=True)
    owner = models.OneToOneField(User, related_name='accounts', on_delete=models.CASCADE)
    balance = models.DecimalField(decimal_places=2, max_digits=20)  # arbitrary maximum digits amount
    # the type used for price is DecimalField because it's better for representing currency

    def deposit(self, amount):
        if amount < 0:
            raise Exception("The deposited amount should not be negative, that's what purchases are for!")
        self.balance += amount
        self.save()


class Operation(models.Model):
    """
    Each change (deposit, purchase, etc..) of Account's balance should be reflected
    in the Operation model for auditing purposes.
    """
    operation_id = models.AutoField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    balance_change = models.DecimalField(decimal_places=2, max_digits=20)  # positive for deposit, negative for purchase

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # call the "real" save() method
        new_balance = self.account.balance + self.balance_change
        if new_balance > 0:
            self.account.balance = new_balance
            self.account.save()


class Book(models.Model):
    """
    Model stores a title of the book and its price.
    """
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=10)


class Purchase(models.Model):
    """
    Model stores data about purchases.
    """
    purchase_id = models.AutoField(primary_key=True)
    books = models.ManyToManyField(Book)  # again, if we're bound to 4 of those models, there needs to be a many-to-many
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE,null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # call the "real" save() method
        transaction_price = self.books.all().aggregate(Sum('price'))
        value = transaction_price['price__sum']
        if value is not None:
            value = value * -1
            if self.account.balance + value < 0:
                raise ValueError("Cannot perform such operation, since the funds are insufficient")
            print("UWAGA ****\n\n ", value)
            self.operation, created = Operation.objects.get_or_create(account=self.account, balance_change=value)
            self.operation.save()

