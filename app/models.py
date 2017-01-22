from . import db


class Doctor(db.Model):
    __tablename__ = 'docs'
    id = db.Column(db.Integer, primary_key=True)
    names = db.Column(db.String(128))
    reg_no = db.Column(db.String(128), unique=True)
    qualifications = db.relationship('Qualification', backref='doc', lazy='dynamic')

    def __repr__(self):
        return '<Doctor %r>' % self.names


class Qualification(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    what = db.Column(db.String(300), nullable=False)
    when = db.Column(db.String(300), nullable=False)
    where = db.Column(db.String(300), nullable=False)
    doc_id = db.Column(db.Integer, db.ForeignKey('docs.id'))

    def __repr__(self):
        return '<Qualification %r>' % self.what