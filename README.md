# Item Catalog
![](https://github.com/egochen/catalogApp/blob/master/screenshots/CatalogAppScreenShot.png "main page")
#### Project Overview
This is an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users have the ability to post, edit and delete their own items.
#### User Guide
To get started, download the `client_secrets.json` file provided separately by me (or you can create your own from console.developers.google.com) and put in the main directory. If you wish to start a fresh database, remove catalog.db and run `python database_setup.py`. Otherwise you can use the provided `catalog.db` as your database.\
The main page will be served at http://localhost:5000
#### API Endpoints
The API for getting all items of all categories is:
http://localhost:5000/categories/items/JSON
#### Authentication & Authorization
Google OpenID Connect is used for user authentication and authorization. In order to add a new category, or add/delete/edit an item under a category, the user must verify their identity through their Google account. A user can only modify the page(s) that they created and not the page(s) created by other users.
#### CRUD Read / Create / Update / Delete
Follow the instructions on the page to perform these actions.
![](https://github.com/egochen/catalogApp/blob/master/screenshots/CatalogEditScreenShot.png "edit page")
