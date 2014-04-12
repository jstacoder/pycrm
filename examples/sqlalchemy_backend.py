# -*- coding: utf-8 -*-
import wtforms
from werkzeug import OrderedMultiDict

from flask import Flask, redirect

from flask_dashed.admin import Admin
from flask_dashed.ext.sqlalchemy import ModelAdminModule, model_form

from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy.orm import aliased, contains_eager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.jinja_env.trim_blocks = True


db = SQLAlchemy(app)
db_session = db.session


# define model classes for Modules
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    zone = db.Column(db.Integer,nullable=False)
    account_num = db.Column(db.String(15),nullable=False)
    #main_contact = db.Column(
    #contacts_group = db.Column
    main_phone = db.Column(db.String(15))
    alt_phone = db.Column(db.String(15))
    #email = db.Column
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


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    zone = db.Column(db.Integer,nullable=False)
    account_num = db.Column(db.String(20),nullable=False)
    password = db.Column(db.String(255))
    is_active = db.Column(db.Boolean())


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

    list_title = 'user list'

    searchable_fields = ['username', 'profile.name', 'profile.location']

    order_by = ('id', 'desc')

    list_query_factory = model.query\
           .outerjoin(profile_alias, 'profile')\
           .options(contains_eager('profile', alias=profile_alias))\

    form_class = UserForm

    def create_object(self):
        user = self.model()
        user.profile = Profile()
        return user


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
    form_class = model_form(Company, db_session)


admin = Admin(app, title="Level2Designs Contact Admin")

security = admin.register_node('/security', 'security', 'security management')

user_module = admin.register_module(UserModule, '/users', 'users',
    'users', parent=security)

group_module = admin.register_module(GroupModule, '/groups', 'groups',
    'groups', parent=security)

company_module = admin.register_module(CompanyModule, '/companies',
    'companies', 'companies')

warehouse_module = admin.register_module(WarehouseModule, '/warehouses',
    'warehouses', 'warehouses', parent=company_module)


@app.route('/')
def redirect_to_admin():
    return redirect('/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
