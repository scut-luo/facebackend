# from . import db

'''
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    # Relationship
    api_keys = db.relationship('APIKey', backref='user', lazy='dynamic')
    facesets = db.relationship('FaceSet', backref='user', lazy='dynamic')


class APIKey(db.Model):
    __tablename__ = 'apikey'
    id = db.Column(db.Integer, primary_key=True)
    apikey = db.Column(db.String(64), unique=True)
    # Relationship
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class FaceSet(db.Model):
    __tablename__ = 'faceset'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True)
    display_name = db.Column(db.String(256))
    # Relationship
    faces = db.relationship('Face', backref='faceset', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Face(db.Model):
    __tablname__ = 'face'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True)
    encoding = db.Column(db.String(2048))
    # Relationship
    faceset_id = db.Column(db.Integer, db.ForeignKey('faceset.id'))
'''
