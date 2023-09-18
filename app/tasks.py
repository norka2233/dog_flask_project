import time, sys, json
from flask import render_template
from rq import get_current_job
from app import create_app, db
from app.models import Post, Task, DogUser
from app.email import send_email


app = create_app()
app.app_context().push()

def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.user.add_notification('task_progres', {'task_id': job.get_id(), 'progress': progress})
        if progress >= 100:
            task.complete = True
        db.session.commit()


def export_posts(id):
    try:
        dog_user = DogUser.query.get(id)
        _set_task_progress(0)
        i = 0
        total_posts = dog_user.posts.count()
        for post in dog_user.posts.order_by(Post.timestamp.asc()):
            data.append({'body': post.body, 'timestamp': post.timestamp.isoformat() + 'Z'})
            time.sleep(5)
            i += 1
            _set_task_progress(100 * i // total_posts)

        send_email('[DogFlaskProject] Your dog blog posts',
                   sender=app.config['ADMINS'][0], recipients=[dog_user.email],
                   text_body=render_template('email/export_posts.txt', dog_user=dog_user),
                   html_body=render_template('email/export_posts.html', dog_user=dog_user),
                   attachments=[('posts.json', 'application/json',
                                 json.dumps({'posts': data}, indent=4))],
                   sync=True)
    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)