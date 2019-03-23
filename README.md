# Item Catalog
![](https://github.com/egochen/catalogApp/blob/master/screenshots/CatalogAppScreenShot.png "main page")
## Project Overview
This is an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users have the ability to post, edit and delete their own items.
## User Guide
To get started, download the `client_secrets.json` file provided separately by me (or you can create your own from console.developers.google.com) and put in the main directory. To get all required libraries, run `pip  install  -r  requirements.txt`.
By running `python run.py`, he main page will be served at http://localhost:5000
## API Endpoints
The API for getting all items of all categories is:
/categories/items/JSON
The API for getting an arbitrary item in the catalog is:
/category/category_name/catalog_name/JSON
## Authentication & Authorization
Google OpenID Connect is used for user authentication and authorization. In order to add a new category, or add/delete/edit an item under a category, the user must verify their identity through their Google account. A user can only modify the page(s) that they created and not the page(s) created by other users.
## CRUD Read / Create / Update / Delete
Follow the instructions on the page to perform these actions.


## Project Rubric

|SECTION|SUB-SECTION|CRITERIA|SPECS. MET?|
|---|---|---|---|
| API Endpoints |  | The project implements a JSON endpoint that serves the same information as displayed in the HTML endpoints for an arbitrary item in the catalog.|Yes|
| CRUD | Read | Does the website read category and item information from a database?|Yes|
| | Create | Does the website include a form allowing users to add new items and correctly processes these forms? |Yes|
| | Update | Does the website include a form to update a record in the database and correctly processes this form? |Yes|
| | Delete | Does the website include a way to delete an item from the catalog? | Yes |
| Authentication & Authorization | Consider Authorization Status prior to Execution | Create, delete and update operations do consider authorization status prior to execution. | Yes |
| | Implement third party authenthication and authorization service | Page implements a third-party authentication & authorization service (like `Google Accounts` or `Mozilla Persona`) instead of implementing its own authentication & authorization spec. | Yes |
| | Show Login and Logout button | Make sure there is a 'Login' and 'Logout' button/link in the project. The aesthetics of this button/link is up to the discretion of the student. | Yes |
| Code Quality | | Code is ready for personal review and neatly formatted and compliant with the Python [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide. | Yes |
| Comments | | Are comments present and effectively explain longer code procedures? | Yes |
