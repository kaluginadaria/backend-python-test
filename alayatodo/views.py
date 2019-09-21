from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    flash, abort, jsonify)

from alayatodo import app


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

    sql = "SELECT * FROM users WHERE username = '%s' AND password = '%s'";
    cur = g.db.execute(sql % (username, password))
    user = cur.fetchone()
    if user:
        session['user'] = dict(user)
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s'" % id)
    todo = cur.fetchone()
    return render_template('todo.html', todo=todo)


@app.route('/todo/<id>/json', methods=['GET'])
def todo_json(id):
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s'" % id)
    todo = cur.fetchone()
    if not todo:
        abort(404)
    return jsonify(dict(todo))


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')
    cur = g.db.execute("SELECT * FROM todos")
    todos = cur.fetchall()
    return render_template('todos.html', todos=todos)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')
    if not request.form.get('description'):
        flash('Description is required.', category='danger')
        return redirect('/todo')
    g.db.execute(
        "INSERT INTO todos (user_id, description) VALUES ('%s', '%s')"
        % (session['user']['id'], request.form.get('description', ''))
    )
    g.db.commit()
    flash('You added todo', category='success')
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    g.db.execute("DELETE FROM todos WHERE id ='%s'" % id)
    g.db.commit()
    flash('You deleted todo', category='success')
    return redirect('/todo')


@app.route('/todo/done/<id>', methods=['POST'])
def todo_done(id):
    g.db.execute("UPDATE todos SET is_completed=1 WHERE id ='%s'" % id)
    g.db.commit()
    return redirect('/todo')


@app.route('/todo/undone/<id>', methods=['POST'])
def todo_undone(id):
    g.db.execute("UPDATE todos SET is_completed=0 WHERE id ='%s'" % id)
    g.db.commit()
    return redirect('/todo')
