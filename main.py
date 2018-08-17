from flask import Flask, request, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
import utils
import file_utils
import json
import logging
import os
from keys import *

HOST = '0.0.0.0'
PORT = 3301

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), 'nyheter.db')
db_uri = 'sqlite:///%s' % db_path
app.config.from_pyfile('app.cfg')
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    message = db.Column('message', db.String)
    photo_id = db.Column('photo_id', db.Integer)
    author = db.Column('author', db.String)
    time = db.Column('time', db.Integer)

    def __init__(self, message, photo_id, author, time=utils.get_time()):
        self.message = message
        self.photo_id = photo_id
        self.author = author
        self.time = time

    def __repr__(self):
        return '(%s, %d, %s, %d)' % (self.message, self.photo_id, self.author, self.time)

    def __str__(self):
        return self.__repr__()


@app.errorhandler(Exception)
def exception_handler(e):
    print(e)
    return utils.get_error_by_code(500)


@app.errorhandler(500)
@app.errorhandler(502)
@app.errorhandler(405)
@app.errorhandler(404)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(400)
def error_handler(e):
    print(e)
    code, _ = utils.get_error_data(e)
    return utils.get_error_by_code(code)


def log_table():
    try:
        print(Post.query.all())
    except Exception as e:
        print(e)


@app.route('/upload', methods=['POST'])
def sticker_upload():
    data = request.form
    if PHOTO not in data:
        return utils.get_error_by_code(400)
    photo = data[PHOTO]
    last_photo_id = file_utils.get_last_id()
    photo_id = last_photo_id + 1
    saved = file_utils.save_photo(photo, photo_id)
    if saved:
        return utils.RESPONSE_FORMAT % str(photo_id)
    else:
        return utils.get_error_by_code(400)


@app.route('/post', methods=["POST"])
def post():
    data = request.form
    if MESSAGE not in data:
        return utils.get_error_by_code(400)
    message = data[MESSAGE]
    photo_id = data[PHOTO_ID] if PHOTO_ID in data else 0
    author = data[AUTHOR] if AUTHOR in data else ""
    new_post = Post(message, photo_id, author)
    db.session.add(new_post)
    db.session.flush()
    db.session.refresh(new_post)
    db.session.commit()
    return utils.RESPONSE_FORMAT % str(new_post.id)


@app.route('/photo/<photo_id>')
def photo_direct(photo_id):
    photo_id = int(photo_id)
    return send_file(file_utils.get_photo_url(photo_id), 'image/png')


@app.route('/')
def feed():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('feed.html', posts=posts)


log_table()
file_utils.init_before()

if __name__ == "__main__":
    db.create_all()
    db.init_app(app)
    app.logger.setLevel(logging.DEBUG)
    app.run(threaded=True, host=HOST, port=PORT)