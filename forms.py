from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, URL
from wtforms.widgets import CheckboxInput, ListWidget

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', 
                             validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ProfileSetupForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Address', validators=[Optional()])
    business_name = StringField('Business Name', validators=[Optional(), Length(max=100)])
    logo = FileField('Business Logo', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'])])
    website = StringField('Website', validators=[Optional(), URL(), Length(max=200)])
    facebook = StringField('Facebook URL', validators=[Optional(), URL(), Length(max=200)])
    instagram = StringField('Instagram URL', validators=[Optional(), URL(), Length(max=200)])
    twitter = StringField('Twitter URL', validators=[Optional(), URL(), Length(max=200)])
    linkedin = StringField('LinkedIn URL', validators=[Optional(), URL(), Length(max=200)])
    submit = SubmitField('Complete Profile')

class MultiCheckboxField(BooleanField):
    widget = CheckboxInput()

class PosterGenerationForm(FlaskForm):
    title = StringField('Poster Title', validators=[DataRequired(), Length(max=200)])
    prompt = TextAreaField('Describe your poster', validators=[DataRequired(), Length(max=1000)])
    
    is_public = BooleanField('Make poster public')
    submit = SubmitField('Generate Poster')
    
    def get_selected_fields(self):
        """Return empty list since profile fields are now handled in editor"""
        return []

class ProfileEditForm(FlaskForm):
    full_name = StringField('Full Name', validators=[Optional(), Length(max=100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Address', validators=[Optional()])
    business_name = StringField('Business Name', validators=[Optional(), Length(max=100)])
    logo = FileField('Business Logo', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'])])
    website = StringField('Website', validators=[Optional(), URL(), Length(max=200)])
    facebook = StringField('Facebook URL', validators=[Optional(), URL(), Length(max=200)])
    instagram = StringField('Instagram URL', validators=[Optional(), URL(), Length(max=200)])
    twitter = StringField('Twitter URL', validators=[Optional(), URL(), Length(max=200)])
    linkedin = StringField('LinkedIn URL', validators=[Optional(), URL(), Length(max=200)])
    submit = SubmitField('Update Profile')
