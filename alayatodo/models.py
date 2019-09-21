from sqlalchemy import Column, Integer, String

from alayatodo import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    todos = db.relationship('Todo', backref='user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.username


class Todo(db.Model):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False)
    description = Column(String(256), nullable=False)
    is_completed = Column(Integer, default=0)

    def __repr__(self):
        return '<Todo %r>' % (self.description)
