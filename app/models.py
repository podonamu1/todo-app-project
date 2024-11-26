from app import db


liker = db.Table(
    'liker',
    db.Column('userId', db.String(100), db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('todoId', db.Integer, db.ForeignKey('todo.id', ondelete='CASCADE'), primary_key=True)
)


class User(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    info = db.Column(db.Text())


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    userId = db.Column(db.String(100),
                       db.ForeignKey('user.id', ondelete='CASCADE'),
                       nullable=False)
    user = db.relationship('User', backref=db.backref('todo_set'))
    time = db.Column(db.DateTime(), nullable=False)
    info = db.Column(db.Text())
    priority = db.Column(db.Integer, nullable=True, server_default='0')
    like = db.relationship('User', secondary=liker, backref=db.backref('liker_set'))


class Detail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todoId = db.Column(db.Integer,
                       db.ForeignKey('todo.id', ondelete='CASCADE'),
                       nullable=False)
    todo = db.relationship('Todo', backref=db.backref('detail_set', cascade='all, delete-orphan'))
    name = db.Column(db.String(200), nullable=False)
    progress = db.Column(db.Float, nullable=False)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todoId = db.Column(db.Integer,
                       db.ForeignKey('todo.id', ondelete='CASCADE'),
                       nullable=False)
    todo = db.relationship('Todo', backref=db.backref('todo_comment_set', cascade='all, delete-orphan'))
    userId = db.Column(db.String(100),
                       db.ForeignKey('user.id', ondelete='CASCADE'),
                       nullable=True)
    user = db.relationship('User', backref=db.backref('user_comment_set'))
    text = db.Column(db.Text(), nullable=False)
    writeTime = db.Column(db.DateTime(), nullable=False)
