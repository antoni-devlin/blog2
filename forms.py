from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired

# Form for adding new posts
class AddEditPost(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    category = SelectField(u'Category', choices=[('cat1', 'Category 1'), ('cat2', 'Category 2'), ('cat3', 'Category 3'), ('cat4', 'Category 4')])
    draft = BooleanField('Draft')
    body = TextAreaField('Content Area')
    submit = SubmitField('Create Post')

# class LoginForm(FlaskForm):
