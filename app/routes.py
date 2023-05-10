from flask import render_template
from app import app


@app.route('/')
@app.route('/index')
def index():
    dog_user = {'username': 'Shnurok'}
    dog_posts = [
        {
            'author': {'username': 'Groshyk'},
            'body': 'Hi everyone!'
        },
        {
            'author': {'username': 'Shkedryk'},
            'body': 'Hi dogs!'
        }
    ]
    return render_template('index.html', title='Homepage', dog_user=dog_user, dog_posts=dog_posts)