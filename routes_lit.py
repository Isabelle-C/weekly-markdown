from flask import Blueprint, render_template, request, redirect, url_for
from models import Lit, db

from datetime import datetime
from dateutil.tz import tzlocal

lit = Blueprint('lit', __name__)


@lit.route('/clear_database2', methods=['POST'])
def clear_database2():
    try:
        Lit.query.delete()  # delete all rows from Task table
        db.session.commit()  # commit the changes
        return render_template('literature.html')
    except:
        return 'There was a problem deleting that task'

@lit.route('/literature', methods=['POST', 'GET'])
def literature():

    now = datetime.now(tzlocal())

    if request.method == 'POST':
        paper_name = request.form['paper_name']
        tag = request.form['tag']
        original_pdf = request.form['original_pdf']
        notes = request.form['notes']

        new_lit = Lit(paper_name=paper_name
                       , tag=tag
                       , original_pdf=original_pdf
                       , notes=notes
                       , date_added=now)
        
        db.session.add(new_lit)
        db.session.commit()

        lits = Lit.query.order_by(Lit.tag).all()
        unique_tags = db.session.query(Lit.tag).distinct().all()

        return render_template('literature.html', lits=lits, unique_tags=unique_tags, now=now)
    else:
        lits = Lit.query.order_by(Lit.tag).all()
        unique_tags = db.session.query(Lit.tag).distinct().all()

        return render_template('literature.html', lits=lits, unique_tags=unique_tags, now=now)


@lit.route('/delete_lit/<int:id>')
def delete_lit(id):
    now = datetime.now(tzlocal())

    lit_to_delete = Lit.query.get_or_404(id)

    try:
        db.session.delete(lit_to_delete)
        db.session.commit()
        return redirect(url_for('lit.literature'))
    except:
        return 'There was a problem deleting that task'

@lit.route('/update_lit/<int:id>', methods=['GET', 'POST'])
def update_lit(id):
    lit = Lit.query.get_or_404(id)
    now = datetime.now(tzlocal())
    
    if request.method == 'POST':
        lit.paper_name = request.form['paper_name']
        lit.tag = request.form['tag']
        lit.original_pdf = request.form['original_pdf']
        lit.notes = request.form['notes']

        try:
            db.session.commit()
            return redirect(url_for('lit.literature'))
        except Exception as e:
            return str(e)

    else:
        return render_template('update_lit.html', lit=lit)