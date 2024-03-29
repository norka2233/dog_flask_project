from app import create_app, db, cli
from app.models import DogUser, Post, Message, Notification,  Task


app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'DogUser': DogUser, 'Post': Post, 'Message': Message,
            'Notification': Notification, 'Task': Task}