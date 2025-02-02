import os
from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

# Secret Key
app.config['SECRET_KEY'] = "my super secret key that no one suppose to know"

# Old SQLite DB
# Add Database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# New MYSQL DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:2002@localhost/our_users'

# Server PostgreSQL DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
# postgresql://flasker_usersdata_user:jrSBrwb1inl7wmyWtO0fSZ2LO57p5jyu@dpg-cufgnl0gph6c7383spsg-a.singapore-postgres.render.com/flasker_usersdata


# Initialize DB
db = SQLAlchemy(app)
# Migrate changes to DB
migrate = Migrate(app, db)

# Create DB Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(100))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Create a String
    def __repr__(self):
        return '<Name %r>' % self.name

# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What is Your Name?!", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a DB Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    submit = SubmitField("Submit")


@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

# Greet User
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()

    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successful")

    return render_template('name.html',
                           name=name,
                           form=form)

# Add Record to MYSQL Database
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        flash("User Added Successful")

    our_users = Users.query.order_by(Users.date_added)

    return render_template('add_user.html',
                           name=name,
                           form=form,
                           our_users=our_users)

# Update MYSQL Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash("User Updated Successful")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update)
        except:
            flash("Error! Looks like there was a problem... try again!!!")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update)
    else:
        return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id=id)
        

# Delete MYSQL Database Record
@app.route('/delete/<int:id>')
def delete(id):
    name = None
    form = UserForm()
    user_to_delete = Users.query.get_or_404(id)

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!!")

        our_users = Users.query.order_by(Users.date_added)

        return render_template('add_user.html',
                           name=name,
                           form=form,
                           our_users=our_users)

    except:
        flash("There was a problem deleting User... Try again!!")
        return render_template('add_user.html',
                           name=name,
                           form=form,
                           our_users=our_users)



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run()