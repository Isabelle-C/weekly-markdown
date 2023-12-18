from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import inspect, extract

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/isabellechen/git-repos/weekly-markdown/tasks.db'
db = SQLAlchemy(app)

with app.app_context():
    db.drop_all()
    db.create_all()

    inspector = inspect(db.engine)
    tables_in_database = inspector.get_table_names()
    print(tables_in_database)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    task_name = db.Column(db.String(200), nullable=False)
    tag = db.Column(db.String(200), nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.Integer, nullable=True)
    done=db.Column(db.Boolean, default=False)
    done_timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/update_done/<int:task_id>', methods=['POST'])
def update_done(task_id):
    task = Todo.query.get_or_404(task_id)
    task.done = request.form.get('done') == 'true'
    if task.done:
        task.done_timestamp = datetime.utcnow()
    else:
        task.done_timestamp = None
    db.session.commit()
    return '', 204

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_name = request.form['task_name']
        tag = request.form['tag']
        due_date_string = request.form['due_date']
        priority = request.form['priority']

        # Convert due_date_string to a datetime object
        due_date = datetime.strptime(due_date_string, "%Y-%m-%d")

        new_task = Todo(task_name=task_name
                        , tag=tag
                        , due_date=due_date
                        , priority=priority)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.filter(Todo.done == False).order_by(Todo.due_date).all()
        unique_tags = db.session.query(Todo.tag).distinct().all()
        now = datetime.utcnow()
        task_weeks = {(task.due_date.date().year, task.due_date.isocalendar()[1]) for task in tasks}
        return render_template('index.html', tasks=tasks, unique_tags=unique_tags, now=now, task_weeks=task_weeks)

from dateutil.relativedelta import relativedelta, MO

@app.route('/week/<int:year>/<int:week>')
def week(year, week):
    start = datetime.strptime(f'{year}-W{int(week )}-1', "%Y-W%W-%w").date()
    end = start + relativedelta(days=+7)
    now = datetime.utcnow()
    tasks = Todo.query.filter(Todo.due_date.between(start, end)).order_by(Todo.due_date).all()

    all_tasks = Todo.query.filter(Todo.done == False).order_by(Todo.due_date).all()
    task_weeks = {(task.due_date.date().year, task.due_date.isocalendar()[1]) for task in all_tasks}
    return render_template('week.html', tasks=tasks, task_week=week, task_year=year, now=now, task_weeks=task_weeks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.task_name = request.form['task_name']
        task.tag = request.form['tag']
        task.due_date = datetime.strptime(request.form['due_date'], "%Y-%m-%d")
        task.priority = request.form['priority']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=task)
if __name__ == "__main__":
    app.run(debug=True, port=5001)
