# -*- coding: utf-8 -*-
import wtforms
from werkzeug import OrderedMultiDict
from sample_data import ContactsDashboard

from flask import Flask, redirect, url_for, render_template, session, request, flash
from functools import wraps

from flask_dashed.views import get_next_or
from flask_dashed.admin import Admin
from flask_dashed.ext.sqlalchemy import ModelAdminModule, model_form

from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy.orm import aliased, contains_eager

from login_utils import encrypt_password, check_password
from flask.views import MethodView

   


app = Flask('level2_pycrm')
app.config['SECRET_KEY'] = 'secret'
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.jinja_env.trim_blocks = True


db = SQLAlchemy(app)
db_session = db.session
#session['logged_in'] = False

def is_email(data):
    'returns true if given data that looks like an email'
    return '@' in data and '.com' in data

def is_unique(itm):
    'returns true if itm is unique email or name in database'


def login_required(test):
    @wraps(test)
    def wrap(*args,**kwargs):
        if 'logged_in' in session: #and not session['logged_in']:
            return test(*args,**kwargs)
        else:
            return redirect(url_for('login',next=request.url))
    return wrap

# view functions
@app.route('/login',methods=["POST","GET"])
def login():
    if request.method.upper() == "POST":
        pw = encrypt_password(request.form['password'])
        username = request.form['username']
        session['logged_in'] = True
        return redirect(url_for('redirect_to_admin'))
    return  render_template('login.html')

@app.route('/register',methods=["POST","GET"])
def register():
    if request.method.upper() == "POST":
        username = request.form['username']
        # check_unique_username(username)
        # error if not
        email = request.form['email']
        # same verification above
        pw1 = encrypt_password(request.form['password'])
        pw2 = request.form['confirm']
        if not check_password(pw2,pw1):
            flash('Passwords didnt match, try again')
            return redirect(url_for('register'))
        else:
            attrs = (
                ('username',username),('email',email),
            )
            return render_template("verify_registration.html",attrs=attrs)
    return render_template('register.html')

@app.route('/verified')
def verified():
            session['logged_in'] = True
            flash('Thank you for sgning up')
            return redirect(url_for('redirect_to_admin'))
    
@app.teardown_context
def auto_logout():
    if session.get('logged_in',False):
        del(session['logged_in'])

# define model classes for Modules

#class Worker(db.Model):
    

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    send_info_email = db.Column(db.Boolean())
    zone = db.Column(db.Integer,nullable=False)
    is_active = db.Column(db.Boolean())
    account_num = db.Column(db.String(20),nullable=False)
    password = db.Column(db.String(255))
    create_password = db.Column(db.Boolean())

    def __unicode__(self):
        return self.username
    def __str__(self):
        return self.__unicode__()


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    zone = db.Column(db.Integer,nullable=False)
    account_num = db.Column(db.String(15),nullable=False)
    main_contact_id = db.Column(db.Integer,db.ForeignKey(User.id))
    contacts_group = db.relationship(User,backref=db.backref("Agencys"))
    main_phone = db.Column(db.String(15))
    alt_phone = db.Column(db.String(15))
    #main_contact_email = db.Column(db.Integer,db.ForeignKey(User.email))
    date_created = db.Column(db.String(10))
    date_modified = db.Column(db.String(10))
    contract_start = db.Column(db.String(10))
    contract_end = db.Column(db.String(10))


    def __unicode__(self):
        return unicode(self.name)

    def __repr__(self):
        return '<Agency %r>' % self.name


class Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey(Company.id))
    company = db.relationship(Company, backref=db.backref("warehouses"))

    def __unicode__(self):
        return self.name   

    def __repr__(self):
        return '<Warehouse %r>' % self.name







class Profile(db.Model):
    id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    company_id = db.Column(db.Integer, db.ForeignKey(Company.id),
        nullable=True)

    user = db.relationship(User, backref=db.backref("profile",
        remote_side=id, uselist=False, cascade="all, delete-orphan"))

    company = db.relationship(Company, backref=db.backref("staff"))

    def __unicode__(self):
        return self.user.username

    

user_group = db.Table(
    'user_group', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    users = db.relationship("User", secondary=user_group,
        backref=db.backref("groups", lazy='dynamic'))

    def __unicode__(self):
        return unicode(self.name)

    def __repr__(self):
        return '<Group %r>' % self.name


db.drop_all()
db.create_all()

group = Group(name="admins")
db_session.add(group)
company = Company(name="Level 2 Designs",zone=1,main_phone='714-783-6369',account_num="4565")
user = User(username="kyle",zone=1,account_num="222",email="kyle@level2designs.com",password="14wp88",is_active=True)
db_session.add(user)
db_session.add(company)
db_session.commit()


UserForm = model_form(User, db_session)#,exclude=['password'])

CompanyForm = model_form(Company, db_session, exclude=['main_contact_id','date_modified'])

class UserForm(UserForm):
    # Embeds OneToOne as FormField
    profile = wtforms.FormField(
        model_form(Profile, db_session, exclude=['user'],
        base_class=wtforms.Form))



class UserModule(ModelAdminModule):
    model = User
    db_session = db_session
    profile_alias = aliased(Profile)

    list_fields = OrderedMultiDict((
        ('id', {'label': 'id', 'column': User.id}),
        ('username', {'label': 'username', 'column': User.username}),
        ('email', {'label': 'email address', 'column': User.email}),
        ('zone', {'label':'Zone', 'column': User.zone}),
        ('account_num',{'label' : 'Account Number','column': User.account_num}),
        ('profile.name', {'label': 'name', 'column': profile_alias.name}),
        ('profile.location', {'label': 'location',
            'column': profile_alias.location}),
    ))

    list_title = 'User list'

    searchable_fields = ['username', 'profile.name', 'zone','account_num','email'] #,'role']

    order_by = ('id', 'desc')

    list_query_factory = model.query\
           .outerjoin(profile_alias, 'profile')\
           .options(contains_eager('profile', alias=profile_alias))\

    form_class = UserForm
    detail_title = 'User Details'

    def create_object(self):
        user = self.model()
        user.profile = Profile()
        return user

class CompanyForm(CompanyForm):
    contact = wtforms.FormField(
        model_form(User, db_session, exclude=['account_num','profile.name','profile.location'],
        base_class=wtforms.Form))

class ContactModule(ModelAdminModule):
    model = User
    db_session = db_session
    form_class = model_form(User, db_session)

class GroupModule(ModelAdminModule):
    model = Group
    db_session = db_session
    form_class = model_form(Group, db_session, only=['name'])


class WarehouseModule(ModelAdminModule):
    model = Warehouse
    db_session = db_session


class CompanyModule(ModelAdminModule):
    model = Company
    db_session = db_session
    form_class = CompanyForm

    def create_object(self):
        company = self.model()
        company.user = User()
        return company


admin = Admin(app, title="Level2Designs Contact Admin", main_dashboard=ContactsDashboard)

security = admin.register_node('/security', 'security', 'contact management')


user_module = admin.register_module(UserModule, '/users', 'users',
    'users', parent=security)

group_module = admin.register_module(GroupModule, '/groups', 'groups',
    'groups', parent=security)

company_module = admin.register_module(CompanyModule, '/companies',
    'companies', 'companies')

contact_module = admin.register_module(ContactModule, '/contacts','contacts','contacts',parent=company_module)

warehouse_module = admin.register_module(WarehouseModule, '/warehouses',
    'warehouses', 'warehouses', parent=company_module)


@app.route('/')
@login_required
def redirect_to_admin():
    return redirect('/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
