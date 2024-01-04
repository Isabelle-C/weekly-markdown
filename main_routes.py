from flask import Blueprint, render_template, request, redirect
from models import Todo, db

from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from dateutil.relativedelta import relativedelta

main = Blueprint('main', __name__)


@main.route('/', methods=['POST', 'GET'])
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
                        , frequency=frequency
                        , date_created=datetime.now(tzlocal()))

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

@main.route('/week/<int:year>/<int:week>')
def week(year, week):
    start = datetime.strptime(f'{year}-W{int(week )}-1', "%Y-W%W-%w").date()
    end = start + relativedelta(days=+7)

    now = datetime.now(tzlocal())
    
    tasks = Todo.query.filter(Todo.due_date.between(start, end)).order_by(Todo.due_date).all()

    all_tasks = Todo.query.filter(Todo.done == False).order_by(Todo.due_date).all()
    task_weeks = {(task.due_date.date().year, task.due_date.isocalendar()[1]) for task in all_tasks}
    return render_template('week.html', tasks=tasks, task_week=week, task_year=year, now=now, task_weeks=task_weeks)