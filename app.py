from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import sys
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) # links SQLAlchemy to our Flask app
migrate = Migrate(app, db)

class Todo(db.Model):
    __tablename__= 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    complete = db.Column(db.Boolean, nullable=False, default=False) #changed to complete
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable = False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description} {self.complete}>' # for debugging purposes
    
class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(), nullable = False)
    todos = db.relationship('Todo', backref='list', lazy = True)

@app.route('/todos/create', methods=['POST']) # post request listener form html post request form
def create_todo(): # this is the route handler for the python decorator above
    error = False
    body = {}
    try:
        description = request.get_json()['description'] # gets back the dictionary made by stringify index.html and keys the key description
        list_id = request.get_json()['list_id']
        todo = Todo(description=description, complete=False, list_id=list_id)
        db.session.add(todo)
        db.session.commit()
        body['id'] = todo.id
        body['complete'] = todo.complete
        body['description'] = todo.description
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error == True:
            abort(400)
    else:
        return jsonify(body)  
    #returns json data back to the client for us
    # return redirect(url_for('index')) #redirect/changes view back to the index route with new todo items - done if you don't use AJAX for asynchronous updates

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    error = False
    try:
        # Todo.query.filter_by(id = todo_id).delete()
        todo = Todo.query.get(todo_id)
        db.session.delete(todo)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({'success': True}) # don't use redirect here because we are using 'DELETE' method instead of 'POST' or 'GET'
# When you use the POST method (HTTP request), the "HTTP response" must be processed on the controller itself
# When you use the DELETE method with javascript DOM (XMLHttpRequest), the "HTTP response" must be processed in the functions of the DOM javascript. It is the javascript DOM that has dominion over the HTML page.

        
@app.route('/todos/<todo_id>/set-complete', methods=['POST'])
def update_todo(todo_id):
    error = False
    try:
        complete = request.get_json()['complete']
        todo = Todo.query.get(todo_id)
        print('Todo: ', todo)
        todo.complete = complete
        db.session.commit()
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return redirect(url_for('index'))
    
@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    error = False
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return '', 200
    # return redirect(url_for('index')) # grabs fresh list of all the todo items and refreshing the entire page. to-do items for us

"""Returns a template html file. render_template specifies html file t render to the user when they visit this route.
Note: flask looks for the folder templates to find html files called with render_template
We can pass in variabes to use in our template into render_template
Flask processes html using a templating engine called Jinja that allows you to embded nonhtml into html files"""
@app.route('/lists/<list_id>') 
def get_list_todos(list_id):
    lists = TodoList.query.all()
    active_list = TodoList.query.get(list_id)
    todos = Todo.query.filter_by(list_id=list_id).order_by('id').all()

    return render_template('index.html', todos=todos, lists=lists, active_list=active_list)
                           
@app.route('/lists/create', methods=['POST'])
def create_list():
    error = False
    body = {}
    try:
        name = request.get_json()['name']
        todolist = TodoList(name=name)
        db.session.add(todolist)
        db.session.commit()
        body['id'] = todolist.id
        body['name'] = todolist.name
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify(body)

@app.route('/lists/<list_id>/delete', methods=['DELETE'])
def delete_list(list_id):
    error = False
    try:
        list = TodoList.query.get(list_id)
        for todo in list.todos:
            db.session.delete(todo)
        db.session.delete(list)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({'success': True})


@app.route('/lists/<list_id>/set-completed', methods=['POST'])
def set_completed_list(list_id):
    error = False
    try:
        list = TodoList.query.get(list_id)
        for todo in list.todos:
            todo.completed = True
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({'success': True})
    
@app.route('/') # visit home page that redirect to list with id of 1
def index():
    return redirect(url_for('get_list_todos', list_id=1))
