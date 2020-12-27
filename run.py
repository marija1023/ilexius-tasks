from flask import Flask, redirect, url_for, flash, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.sqlite3'
app.config['SECRET_KEY'] = 'random string'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Employee(db.Model):
    __tablename__ = 'employee'
    id = db.Column('employee_id', db.String(50), primary_key=True)
    active = db.Column(db.Boolean, default=True)

    def __init__(self, id):
        self.id = id
        self.active = True

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

#create all db tables --> init
@app.before_first_request
def create_tables():
    # from models import ContactModel
    db.create_all()

@app.route('/')
def show_all():
    return render_template('show_all.html', employees=Employee.query.all())

@app.route('/new', methods=['POST', 'GET'])
def new():
    if request.method == 'POST':
        employee = Employee(request.form['employee_id'])
        db.session.add(employee)
        db.session.commit()
        flash('Record was added successfully!')
        return redirect(url_for('show_all'))

    return render_template('new.html')

if __name__ == '__main__':
    app.run(debug=True)