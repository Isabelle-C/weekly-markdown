from flask import Blueprint, render_template, request, redirect
from models import Todo, db


from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from dateutil.relativedelta import relativedelta

todo = Blueprint('todo', __name__)


@todo.route('/update_done/<int:task_id>', methods=['POST'])
def update_done(task_id):
    task = Todo.query.get_or_404(task_id)
    task.done = request.form.get('done') == 'true'
    if task.done:
        task.done_timestamp = datetime.now(tzlocal())
    else:
        task.done_timestamp = None
    db.session.commit()
    return '', 204

@todo.route('/clear_database', methods=['POST'])
def clear_database():
    try:
        Todo.query.delete()  # delete all rows from Task table
        db.session.commit()  # commit the changes
        return redirect('/')
    except:
        return 'There was a problem deleting that task'
    
@todo.route('/completed')
def completed():
    tasks = Todo.query.filter(Todo.done == True).order_by(Todo.due_date).all()
    now = datetime.now(tzlocal())
    return render_template('completed.html', tasks=tasks, now=now)

@todo.route('/delete/<int:id>')
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

@todo.route('/update/<int:id>', methods=['GET', 'POST'])
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

@todo.route('/search', methods=['GET'])
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
