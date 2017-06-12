
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


blog_app = Flask(__name__)
blog_app.config.from_object('config')
db = SQLAlchemy(blog_app)
lm = LoginManager()
lm.init_app(blog_app)
lm.login_view = 'login'

from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD

if not blog_app.debug:
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'microblog failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    blog_app.logger.addHandler(mail_handler)

if not blog_app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    blog_app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    blog_app.logger.addHandler(file_handler)
    blog_app.logger.info('microblog startup')

from app import views, models