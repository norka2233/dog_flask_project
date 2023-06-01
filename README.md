##Welcome to my project created mainly with Python and Flask framework.Used [Miguel Grinberg MegaFlaskTutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) as a base to dig dipper into Flask.

### 1. Check if you have Python3  installed
`$ python3`

If not, please use [Python documentation](https://www.python.org/downloads/) to install.


### 2.Better to create virtual environment to launch the project
`$ python3 -m venv venv`

`$ venv/bin/activate`

You should see environment activated by having venv name in command prompt window, for me it is 'venv'.

 `$ (venv) ...`

### 3. Install all packages and modules from the project use:

`$ (venv) pip install -r requirements.txt`

###4. Wait all packages be installed and run the project with:

`$ (venv) flask run`

###5. To create and run app with data the database is needed. Run: 

`flask db init`

`flask db migrate`

`flask db upgrade`
### Enjoy the app!


13 chapter
pybabel extract -F babel.cfg -k _l -o messages.pot .



