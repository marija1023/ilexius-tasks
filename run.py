from flask import Flask, redirect, url_for, flash, render_template, request
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager, current_user, login_user
# from flask.Flask import g

from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, validators, ValidationError

from flask_admin import BaseView, expose, Admin
# from flask_appbuilder import ModelView
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.sqlite3'
app.config['SECRET_KEY'] = 'random string'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column('user_id', db.String(50), primary_key=True)
    active = db.Column(db.Boolean, default=True)
    login_counts = db.Column(db.Integer)

    def __init__(self, id):
        self.id = id
        self.active = True
        self.authenticated = True
        self.login_counts = 0

    def loged_in(self):
        self.login_counts += 1

    def is_active(self):
        return self.active

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

class Unique(object):
    """ validator that checks field uniqueness """
    def __init__(self, model, field, message=None):
        self.model = model
        self.field = field
        if not message:
            message = 'this element already exists'
        self.message = message

    def __call__(self, form, field):         
        check = self.model.query.filter(self.field == field.data).first()
        if check:
            raise ValidationError(self.message)

class Exist(object):
    """ validator that checks field existence """
    def __init__(self, model, field, message=None):
        self.model = model
        self.field = field
        if not message:
            message = 'this element doesn\'t exists'
        self.message = message

    def __call__(self, form, field):         
        check = self.model.query.filter(self.field == field.data).first()
        if not check:
            raise ValidationError(self.message)

class UserForm(FlaskForm):
    user_id = TextField('User id', validators=[validators.Optional(), Unique(User, User.id)])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    user_id = TextField('User id', validators=[validators.Optional(), Exist(User, User.id)])
    submit = SubmitField('Submit')

class AdminModelView(ModelView):
    form_columns = ('id', 'active','login_counts')
    column_searchable_list = ('id')
    
    form_widget_args = {
        'id': {
            'readonly': True
        }
    }

    def __init__(self, session, **kwargs):
        super(AdminModelView, self).__init__(User, session, **kwargs)

class AdminSettings(BaseView):
    @expose('/login', methods=['POST', 'GET'])
    def login(self):
        error = None
        form = LoginForm()

        if request.method == 'POST':
            if form.validate() == False:
                flash("Validation failed ()")
                return render_template('login.html', form=form)
            else:
                user = User.query.filter_by(id=request.form['user_id']).first()
                user.loged_in()
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for('show_all'))

        return render_template('login.html', form=form)

admin = Admin(name="microadmin")
admin.init_app(app)
admin.add_view(AdminModelView(db.session))
admin.add_view(AdminSettings(name='Admin Settings', endpoint='crud'))

#create all db tables --> init
@app.before_first_request
def create_tables():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    # g.user = current_user
    return User.query.filter_by(id = user_id).first()

@app.route('/')
def show_all():
    return render_template('show_all.html', users=User.query.all(), current_user=current_user)

@app.route('/new', methods=['POST', 'GET'])
def new():
    form = UserForm()

    if request.method == 'POST':
        if form.validate() == False:
            flash("Validation failed ()")
            return render_template('new.html', form=form)
        else:
            user = User(request.form['user_id'])
            user.loged_in()
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Record was added successfully!')
            return redirect(url_for('show_all'))

    return render_template('new.html', form=form)

# @app.route('/login', methods=['POST', 'GET'])
# def login():
#     error = None
#     form = LoginForm()

#     if request.method == 'POST':
#         if form.validate() == False:
#             flash("Validation failed ()")
#             return render_template('login.html', form=form)
#         else:
#             user = User.query.filter_by(id=request.form['user_id']).first()
#             user.loged_in()
#             db.session.commit()
#             login_user(user, remember=True)
#             return redirect(url_for('show_all'))

#     return render_template('login.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)