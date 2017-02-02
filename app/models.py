from . import db
from datetime import datetime


class Doctor(db.Model):
    __tablename__ = 'docs'
    id = db.Column(db.Integer, primary_key=True)
    names = db.Column(db.String(128))
    reg_no = db.Column(db.String(128), unique=True)
    qualifications = db.relationship('Qualification', backref='doc', lazy='dynamic')

    def __repr__(self):
        return '<Doctor %r>' % self.names


class QueryLog(db.Model):
    __tablename__ = 'query_log'
    id = db.Column(db.Integer, primary_key=True)
    phoneNumber = db.Column(db.String(20))
    query = db.Column(db.String(128))
    ip_address = db.Column(db.String(20))
    browser = db.Column(db.String(40))
    operating_system = db.Column(db.String(40))
    channel = db.Column(db.String(20))
    query_date = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return '<Query From  %r>' % self.phoneNumber


class Doc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    names = db.Column(db.String(128))
    reg_date = db.Column(db.Date)
    reg_no = db.Column(db.String(10), unique=True)
    address = db.Column(db.String(128))
    qualifications = db.Column(db.String(100))
    specialty = db.Column(db.String(100))
    sub_speciality = db.Column(db.String(100))

    def __repr__(self):
        return '<Doctor %r>' % self.names


class Nhif(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True)
    hospital = db.Column(db.String(128))
    location = db.Column(db.String(30))
    cover = db.Column(db.String(30))

    def __repr__(self):
        return '<NHIF %r>' % self.hospital


class Qualification(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    what = db.Column(db.String(300), nullable=False)
    when = db.Column(db.String(300), nullable=False)
    where = db.Column(db.String(300), nullable=False)
    doc_id = db.Column(db.Integer, db.ForeignKey('docs.id'))

    def __repr__(self):
        return '<Qualification %r>' % self.what