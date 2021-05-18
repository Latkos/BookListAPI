from django.conf import settings
from django.db import models


class Account(models.Model):
    """
    Account model holds current balance of every user.
    """
    pass


class Operation(models.Model):
    """
    Each change (deposit, purchase, etc..) of Account's balance should be reflected
    in the Operation model for auditing purposes.
    """
    pass


class Book(models.Model):
    """
    Model stores a title of the book and its price.
    """
    pass


class Purchase(models.Model):
    """
    Model stores data about purchases.
    """
    pass

