from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from datetime import datetime

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(user_id)



class Permission:
    BOOK_FLIGHTS_AS_CUST = 0x01
    BOOK_FLIGHTS_AS_AGENT = 0x02
    MANAGE_AIRLINES = 0x04
    ADMINISTER = 0x80
