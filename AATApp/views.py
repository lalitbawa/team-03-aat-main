from flask_admin.contrib.sqla import ModelView
import flask_login as login
from AATApp.models import User
from flask import redirect, url_for, request


class AdminView(ModelView):
    def is_accessible(self):
        if login.current_user.is_authenticated:
            if login.current_user.get_id():
                user = User.query.get(login.current_user.get_id())
                return user.is_admin
        return False

    def inaccessible_callback(self):
        # redirect to homepage if user doesn't have access
        return redirect(url_for('home'))

    column_list = ('id', 'username', 'email', 'is_student', 'is_admin')
