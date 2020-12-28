from flask import Flask, redirect, url_for, flash, render_template, request
from flask_sqlalchemy import SQLAlchemy

from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, validators, ValidationError

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.sqlite3'
app.config['SECRET_KEY'] = 'random string'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column('user_id', db.String(50), primary_key=True)
    active = db.Column(db.Boolean, default=True)

    def __init__(self, id):
        self.id = id
        self.active = True

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

class UserForm(FlaskForm):
    user_id = TextField('User id', validators=[validators.Optional(), Unique(User, User.id)])
    submit = SubmitField('Submit')

#create all db tables --> init
@app.before_first_request
def create_tables():
    # from models import ContactModel
    db.create_all()

@app.route('/')
def show_all():
    return render_template('show_all.html', users=User.query.all())

@app.route('/new', methods=['POST', 'GET'])
def new():
    form = UserForm()

    if request.method == 'POST':
        if form.validate() == False:
            flash("Validation failed ()")
            return render_template('new.html', form=form)
        else:
            user = User(request.form['user_id'])
            db.session.add(user)
            db.session.commit()
            flash('Record was added successfully!')
            return redirect(url_for('show_all'))

    return render_template('new.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)