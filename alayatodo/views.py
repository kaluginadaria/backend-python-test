from flask import (
    redirect,
    render_template,
    request,
    session,
    flash, abort)

from alayatodo import app, db
from alayatodo.models import User, Todo
from alayatodo.schemas import todo_schema, user_schema


@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username, password=password).first()
    if user:
        session['user'] = user_schema.dump(user).data
        session['logged_in'] = True
        return redirect('/todo')
    else:
        flash('Sign up to create your todos')
        # todo redirect to signup page
        return redirect('/login')



@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    todo = Todo.query.get(id)
    return render_template('todo.html', todo=todo)


@app.route('/todo/<id>/json', methods=['GET'])
def todo_json(id):
    todo = Todo.query.get(id)
    if not todo:
        abort(404)
    return todo_schema.dump(todo)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')
    todos = Todo.query.all()
    return render_template('todos.html', todos=todos)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')
    if not request.form.get('description'):
        flash('Description is required.', category='danger')
        return redirect('/todo')
    new_todo = Todo(user_id=session['user']['id'], description=request.form.get('description'))
    db.session.add(new_todo)
    db.session.commit()
    flash('You added todo', category='success')
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    Todo.query.filter_by(id=id).delete()
    db.session.commit()
    flash('You deleted todo', category='success')
    return redirect('/todo')


@app.route('/todo/done/<id>', methods=['POST'])
def todo_done(id):
    todo = Todo.query.filter_by(id=id).first()
    todo.is_completed = 1
    db.session.commit()
    return redirect('/todo')


@app.route('/todo/undone/<id>', methods=['POST'])
def todo_undone(id):
    todo = Todo.query.filter_by(id=id).first()
    todo.is_completed = 0
    db.session.commit()
    return redirect('/todo')
