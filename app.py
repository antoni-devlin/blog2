from flask import Flask, url_for, render_template, request, flash, redirect
from slugify import slugify
from flask_sqlalchemy import *
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, logout_user, login_user, current_user, login_required, login_manager
from datetime import datetime
from forms import AddEditPost, LoginForm, RegistrationForm
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
import os

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "blogdatabase.db"))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sjshlaiyeiruhkjgavksnlkvnslvsnlvsnlvnsdh536574988tufaa7v02j4ueyv7iu2'
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
ckeditor = CKEditor(app)

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
        if not target.slug:
            target.slug = slugify(value)

event.listen(Post.title, 'set', Post.generate_slug, retval=False)

class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

#Home Page Route
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}

@app.route('/')
@app.route('/index')
def index():
    title = 'Antoni Devlin | Blog'
    posts = Post.query.all()
    return render_template('index.html', posts=posts, title=title)

#Add New Post Route
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_post():
    form = AddEditPost()
    if form.validate_on_submit():
        post = Post(title = form.title.data, category = form.category.data, draft = form.draft.data, body = form.body.data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html', form=form)

# Edit Existing Post
@app.route('/edit/<string:slug>', methods=['GET', 'POST'])
@login_required
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    form = AddEditPost(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.category = form.category.data
        post.draft = form.draft.data
        post.body = form.body.data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html', form=form, title='Edit Post')

@app.route('/delete/<string:slug>')
@login_required
def delete_post(slug):
    Post.query.filter_by(slug=slug).delete()
    db.session.commit()
    return redirect(url_for('index'))


# Navigate to post by slug
@app.route('/post/<string:slug>')
def byslug(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    return render_template("post.html", post=post, slug=slug)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

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
