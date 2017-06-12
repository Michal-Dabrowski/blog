
from flask_wtf import Form
from wtforms import StringField, BooleanField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed
from app.models import User

class LoginForm(Form):
    remember_me = BooleanField('remember_me', default=False)
    password = PasswordField('password', validators=[DataRequired()])
    login = StringField('login', validators=[DataRequired()])

class RegisterForm(Form):
    password = PasswordField('password',
                             validators=[DataRequired(),
                                         EqualTo('confirm', message="Passwords must be equal!")
                                         ]
                             )
    confirm = PasswordField("Confirm your password.")
    login = StringField('login', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])

    def validate(self):
        if not Form.validate(self):
            return False

        if User.query.filter_by(nickname=self.login.data).first() is not None:
            version = 2
            while True:
                new_nickname = self.login.data + str(version)
                if User.query.filter_by(nickname=new_nickname).first() is None:
                    break
                version += 1
            self.login.errors.append('This nickname is already in use. Please choose another one, for example: {}'.format(new_nickname))
            return False

        if User.query.filter_by(email=self.email.data).first() is not None:
            self.email.errors.append('This email is already in use. Please choose another one.')
            return False
        return True

class EditForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])
    avatar = FileField()

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user != None:
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True

class PostForm(Form):
    post = StringField('post', validators=[DataRequired()])

class MessageForm(Form):
    message = StringField('message', validators=[DataRequired()])

class CompareFiles(Form):
    file_1 = FileField('file_1', validators=[FileRequired(), FileAllowed(['csv'], message="Only CSV files!")])
    file_2 = FileField('file_2', validators=[FileRequired(), FileAllowed(['csv'], message="Only CSV files!")])