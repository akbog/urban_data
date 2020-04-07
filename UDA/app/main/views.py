from flask import render_template, session, redirect, url_for
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from ..models import Permission
from .. import db
from . import main

from dateutil.relativedelta import relativedelta

@main.route('/', methods = ['GET','POST'])
def index():
    return render_template('index.html', permissions = Permission)
