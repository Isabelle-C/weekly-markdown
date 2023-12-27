from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dateutil.tz import tzlocal

db = SQLAlchemy()

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default= datetime.now(tzlocal()))
    
    task_name = db.Column(db.String(200), nullable=False)
    tag = db.Column(db.String(200), nullable=True)
    frequency = db.Column(db.String(200), default='Once')
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.Integer, nullable=True)
    done=db.Column(db.Boolean, default=False)
    done_timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return '<Task %r>' % self.id

class Lit(db.Model):
    __bind_key__ = 'lit'
    id = db.Column(db.Integer, primary_key=True)
    date_added = db.Column(db.DateTime, default= datetime.now(tzlocal()))
    paper_name = db.Column(db.String(200), nullable=True)
    tag = db.Column(db.String(200), nullable=True)
    original_pdf = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.String(200), nullable=True)