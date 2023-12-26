from flask import Flask, render_template, url_for, request, redirect, session, g, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from dateutil.relativedelta import relativedelta, MO

from sqlalchemy import inspect, extract
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/isabellechen/git-repos/weekly-markdown/tasks.db'
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)

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

from flask import request

@app.route('/search', methods=['GET'])
def search():
    task_name = request.args.get('task_name', '')
    tag = request.args.get('tag', '')
    due_date = request.args.get('due_date', '')
    priority = request.args.get('priority', '')
    frequency = request.args.get('frequency', '')

    # Convert due_date to a datetime object
    if due_date:
        due_date = datetime.strptime(due_date, "%Y-%m-%d")

    # Build the query
    query = Todo.query
    if task_name:
        query = query.filter(Todo.task_name.like(f'%{task_name}%'))
    if tag:
        query = query.filter(Todo.tag == tag)
    if due_date:
        query = query.filter(Todo.due_date == due_date)
    if priority:
        query = query.filter(Todo.priority == priority)
    if frequency:
        query = query.filter(Todo.frequency == frequency)

    # Execute the query and get the results
    tasks = query.all()
    now = datetime.now(tzlocal())

    return render_template('search_results.html', tasks=tasks, now=now)

@app.route('/update_done/<int:task_id>', methods=['POST'])
def update_done(task_id):
    task = Todo.query.get_or_404(task_id)
    task.done = request.form.get('done') == 'true'
    if task.done:
        task.done_timestamp = datetime.now(tzlocal())
    else:
        task.done_timestamp = None
    db.session.commit()
    return '', 204

@app.route('/clear_database', methods=['POST'])
def clear_database():
    try:
        Todo.query.delete()  # delete all rows from Task table
        db.session.commit()  # commit the changes
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/completed')
def completed():
    tasks = Todo.query.filter(Todo.done == True).order_by(Todo.due_date).all()
    now = datetime.now(tzlocal())
    return render_template('completed.html', tasks=tasks, now=now)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_name = request.form['task_name']
        tag = request.form['tag']
        due_date_string = request.form['due_date']
        priority = request.form['priority']
        frequency = request.form['frequency']

        # Convert due_date_string to a datetime object
        due_date = datetime.strptime(due_date_string, "%Y-%m-%d")

        new_task = Todo(task_name=task_name
                        , tag=tag
                        , due_date=due_date
                        , priority=priority
                        , frequency=frequency)

        try:
            if frequency == 'once':
                db.session.add(new_task)
            else:
                if frequency == 'daily':
                    delta = timedelta(days=1)
                elif frequency == 'weekly':
                    delta = timedelta(days=7)
                elif frequency == 'yearly':
                    delta = timedelta(weeks=52)

                end_date = due_date + timedelta(weeks=52)  # one year from now
                while due_date < end_date:
                    new_task = Todo(task_name=task_name
                        , tag=tag
                        , due_date=due_date
                        , priority=priority
                        , frequency=frequency)
                    db.session.add(new_task)
                    if frequency == 'monthly':
                        due_date += relativedelta(months=1)
                    else:
                        due_date += delta

            db.session.commit()
            return redirect('/')
        except Exception as e:
            return 'There was an issue adding your task: ' + str(e)
    else:
        tasks = Todo.query.filter(Todo.done == False).order_by(Todo.due_date).all()
        unique_tags = db.session.query(Todo.tag).distinct().all()

        task_weeks = {(task.due_date.date().year, task.due_date.isocalendar()[1]) for task in tasks}
        
        now = datetime.now(tzlocal())

        return render_template('index.html', tasks=tasks, unique_tags=unique_tags, now=now, task_weeks=task_weeks)

@app.route('/week/<int:year>/<int:week>')
def week(year, week):
    start = datetime.strptime(f'{year}-W{int(week )}-1', "%Y-W%W-%w").date()
    end = start + relativedelta(days=+7)

    now = datetime.now(tzlocal())
    
    tasks = Todo.query.filter(Todo.due_date.between(start, end)).order_by(Todo.due_date).all()

    all_tasks = Todo.query.filter(Todo.done == False).order_by(Todo.due_date).all()
    task_weeks = {(task.due_date.date().year, task.due_date.isocalendar()[1]) for task in all_tasks}
    return render_template('week.html', tasks=tasks, task_week=week, task_year=year, now=now, task_weeks=task_weeks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        if task_to_delete.frequency != 'once':
            # Delete all tasks with the same name
            Todo.query.filter(Todo.task_name == task_to_delete.task_name, Todo.frequency == task_to_delete.frequency).delete()
        else:
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
        new_frequency = request.form['frequency']

        if task.frequency != new_frequency:
            # Delete all tasks with the same name
            Todo.query.filter(Todo.task_name == task.task_name, Todo.frequency == task.frequency).delete()

            new_task = Todo(task_name=request.form['task_name']
                        , tag=request.form['tag']
                        , due_date=datetime.strptime(request.form['due_date'], "%Y-%m-%d")
                        , priority=request.form['priority']
                        , frequency=new_frequency)

            if new_frequency == 'once':
                db.session.add(new_task)
            else:
                if new_frequency == 'daily':
                    delta = timedelta(days=1)
                elif new_frequency == 'weekly':
                    delta = timedelta(days=7)
                elif new_frequency == 'yearly':
                    delta = timedelta(weeks=52)

                due_date = datetime.strptime(request.form['due_date'], "%Y-%m-%d")

                end_date = due_date + timedelta(weeks=52)  # one year from now 
                while due_date < end_date:
                    new_task = Todo(task_name=request.form['task_name']
                        , tag=request.form['tag']
                        , due_date=due_date
                        , priority=request.form['priority']
                        , frequency=new_frequency)
                    db.session.add(new_task)
                    
                    if new_frequency == 'monthly':
                        due_date += relativedelta(months=1)
                    else:
                        due_date += delta

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=task)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
