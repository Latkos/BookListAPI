## DESCRIPTION
This application is an online book store, which allows users to buy books with money deposited on their accounts.

Specific instructions I had to follow are described at the end of this README.

------------------------------------------------

## HOW TO RUN:

The API is deployed to Heroku

* You can access the API at https://api-book-list.herokuapp.com/
![image](https://user-images.githubusercontent.com/48084189/119548470-89d34300-bd96-11eb-9438-44777c2fbce1.png)

* The books list is at: https://api-book-list.herokuapp.com/books/
![image](https://user-images.githubusercontent.com/48084189/119548611-af604c80-bd96-11eb-83cc-b029319bb60c.png)

* You can buy books at: https://api-book-list.herokuapp.com/books/buy/ (in order to buy e.g. books with ID 1 and 2, type in {"books":[1,2]})
![image](https://user-images.githubusercontent.com/48084189/119548687-bf782c00-bd96-11eb-8d63-6d056d12d064.png)

Remember, that to buy books you need authentication, sample account created for showcase purposes:

**LOGIN: sample_user**

**PASSWORD: book_pass**

The accounts are tied to Django accounts, so if you try to create another, it won't work. You can change the current balance though, as it is just a showcase simulation.

------------------------------------------------

## HOW TO RUN IN PRODUCTION:

First install the dependencies if you haven't got them already (I did not use any extra packages myself)
```
pip install -r requirements.txt
```
Migrations are ready to save your time. You can just run
```
python manage.py migrate
```
And then the application can be started with
```
python manage.py runserver
```

The second migration, named "0002_populate_database_sample_values.py" will create 5 sample books, one user and one account.

After migrations, in order to use the app's functions which are limited to authenticated users (as it was required), you may log in with those credentials:

**LOGIN: sample_user**

**PASSWORD: book_pass**

If you wish to create a new account, you will need to create a new Django user from Django console. Then you can access an extra "/accounts/" endpoint to create an account with the balance you pick.

The test coverage for "views.py" and "models.py" is both 100% and you may find them in tasks/tests module.
They were created using Pylint.

------------------------------------------------

## TASK:


The task consists of 3 parts:
1. Implement necessary fields and connections between models in file `tasks/models.py`.
2. Implement an API endpoint `/books/` which lists all available books (id, title and price).
3. Implement an API endpoint `/books/buy/` which accepts an object `{“books”: [ids…]}` and allows user to buy available books using previously deposited funds. Successful response should include array with ids of books and total cost.

Specific requirements:
* Everyone can view books, but only authenticated users can buy them.
* Total cost of purchase should be deducted from user’s account. If amount exceeds total balance, then endpoint should return an error message.
* You should store information about every purchase in a model `Purchase`.
* Try to implement code responsible for spending user’s balance in a reusable fashion.
* User’s balance and prices are expressed in a fiat currency, thus they can have fractional part.
* Include at least basic tests of your code. You may need to write a simple mock of deposit functionality.
* Cover as many edge cases as you can find.
* Explain in comments any assumptions and decisions you made.

