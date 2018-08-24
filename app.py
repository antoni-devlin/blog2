from flask import Flask, url_for, render_template, request, flash, redirect
from slugify import slugify
from flask_sqlalchemy import SQLAlchemy, event
from flask_migrate import Migrate
from datetime import datetime
from forms import *
import os

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "blogdatabase.db"))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sjshlaiyeiruhkjgavksnlkvnslvsnlvsnlvnsdh536574988tufaa7v02j4ueyv7iu2'
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Post(db.Model):

    __tablename__ = 'posts'

    id = db.Column(db.Integer(), primary_key=True)
    date_posted = db.Column(db.DateTime(), index = True, default = datetime.utcnow)
    title = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, default = id, nullable=False)
    category = db.Column(db.String(80))
    draft = db.Column(db.Boolean(), default = True)
    body = db.Column(db.Text())

    def __repr__(self):
        return '<Post {}>'.format(self.body)
# Automatic Slug generation (using slugify)
    @staticmethod
    def generate_slug(target, value, oldvalue, initiator):
        if value and (not target.slug or value  != oldvalue):
            target.slug = slugify(value)

event.listen(Post.title, 'set', Post.generate_slug, retval=False)






# Slugify test
# txt = "This is a test ---"
# r = slugify(txt)
# self.assertEqual(r, "this-is-a-test")

@app.route('/')
@app.route('/index')
def index():

    title = 'Antoni Devlin | Blog'
    posts = Post.query.all()
    return render_template('index.html', posts=posts, title=title)

#Add New Post Route
@app.route('/add', methods=['GET', 'POST'])
def add_post():
    form = AddEditPost()
    if form.validate_on_submit():
        post = Post(title = form.title.data, category = form.category.data, draft = form.draft.data, body = form.body.data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html', form=form)

# Edit Existing Post
@app.route('/edit/<string:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = Post.query.get(id)
    form = AddEditPost(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.category = form.category.data
        post.draft = form.draft.data
        post.body = form.body.data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html', form=form)


@app.route('/posts/<int:id>')
def showpost(id):
    post = Post.query.get(id)
    return render_template("post.html", post=post, pid=id )


@app.route('/login')
def login():
    title = 'Login'
    return render_template('login.html', title=title)

@app.route('/contact')
def contact():
    title = 'Contact'
    return render_template('contact.html', title=title)

@app.route('/about')
def about():
    title = 'About'
    return render_template('about.html', title=title)

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    title = 'Not Found'
    return render_template('404.html', title=title), 404
