from functools import wraps

from flask import (
    redirect,
    render_template,
    request,
    session,
    flash, abort, url_for)
from flask_paginate import get_page_parameter, Pagination

from alayatodo import app, db, bcrypt, TODOS_PER_PAGE
from alayatodo.models import User, Todo
from alayatodo.schemas import todo_schema, user_schema


def get_user_todo(obj_id):
    todo = Todo.query.filter_by(id=obj_id, user_id=session['user']['id']).first()
    if not todo:
        abort(404)
    return todo


def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login', next=request.url))
        return func(*args, **kwargs)

    return decorated_function


@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        session['user'] = user_schema.dump(user).data
        session['logged_in'] = True
        return redirect('/todo')
    else:
        flash('Wrong username and/or password', category='danger')
        return redirect('/login')


@app.route('/signup', methods=['POST'])
def signup_POST():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user:
        flash('This username is already in use', category='danger')
        return redirect('/signup')
    if username and password:
        hashed_password = bcrypt.generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        if new_user:
            session['user'] = user_schema.dump(new_user).data
            session['logged_in'] = True
            return redirect('/todo')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
@login_required
def todo(id):
    todo = get_user_todo(id)
    return render_template('todo.html', todo=todo)


@app.route('/todo/<id>/json', methods=['GET'])
@login_required
def todo_json(id):
    todo = get_user_todo(id)
    return todo_schema.dump(todo)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
@login_required
def todos():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    todos_page = Todo.query.filter_by(user_id=session['user']['id']) \
        .order_by(Todo.created_dt.desc()) \
        .paginate(page=page, per_page=TODOS_PER_PAGE)
    pagination = Pagination(page=page, per_page=TODOS_PER_PAGE, css_framework='foundation',
                            total=todos_page.total)

    return render_template('todos.html', todos=todos_page.items, pagination=pagination, )


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
@login_required
def todos_POST():
    if not request.form.get('description'):
        flash('Description is required.', category='danger')
        return redirect('/todo')
    new_todo = Todo(user_id=session['user']['id'], description=request.form.get('description'))
    db.session.add(new_todo)
    db.session.commit()
    flash('You added todo', category='success')
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
@login_required
def todo_delete(id):
    todo = get_user_todo(id)
    db.session.delete(todo)
    db.session.commit()
    flash('You deleted todo', category='success')
    return redirect('/todo')


@app.route('/todo/undone/<id>', endpoint='undone', methods=["POST"])
@app.route('/todo/done/<id>', endpoint='done', methods=["POST"])
@login_required
def todo_completion(id):
    is_completed = 1 if request.endpoint == 'done' else 0
    todo = get_user_todo(id)
    todo.is_completed = is_completed
    db.session.commit()
    return redirect('/todo')
