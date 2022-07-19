import sqlite3
#from bottle import route, run, debug, template, request, static_file, error
from bottle import Bottle, run, debug, template, request, static_file, error

from bottle import jinja2_template

from jinja2 import Template
from wtforms import Form, BooleanField, StringField, validators

# only needed when you run Bottle on mod_wsgi
#from bottle import default_app

class MyForm(Form):
    task = StringField('Task', validators=[validators.input_required()])

app = Bottle()

@app.route('/todo')
def todo_list():

    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("select id, task from todo where status like '1'")
    result = c.fetchall()
    c.close()

    #debug
    for row in result:
        print('row is', row[0])
        
    #output = template('make_table', rows=result)
    output = jinja2_template('make_table.html', rows=result)

    return output

@app.route('/new', method='GET')
def new_item():

    form = MyForm(request.GET)

    if request.GET.save:

        if form.validate():
            new = request.GET.task.strip() #already utf8 encode
            conn = sqlite3.connect('todo.db')

            c = conn.cursor()
            c.execute("insert into todo (task, status) values (?, ?)", (new, 1))
            new_id = c.lastrowid

            conn.commit()
            c.close()

            return '<p>The new task was inserted into the database, the ID is %s</p>'
    
    else:
        #return template('new_task.tpl')
        return jinja2_template('new_task.html', form=form)

@app.route('/item/<item:re:[0-9]+>')
def show_item(item):
	
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT task FROM todo WHERE id LIKE ?", (item,))
    result = c.fetchall()
    c.close()

    if not result:
        return 'This item number does not exist!'
    else:
        return 'Task: %s' % result[0]

@app.route('/edit/<no:int>', mehtod='GET')
def edit_item(no):

    if request.GET.save:
       edit = request.GET.task.strip() 
       status = request.GET.status.strip()

       if status == 'open':
           status = 1
       else:
           status = 0

       conn = sqlite3.connect('todo.db')
       c = conn.cursor()
       c.execute("UPDATE todo SET task = ?, status = ? where id like  ?", (edit, status, no))
       conn.commit()

       return '<p>The item number %s was successfully updated</p>' % no

    else:
       conn = sqlite3.connect('todo.db')
       c = conn.cursor()
       c.execute("SELECT task FROM todo where id like ?", (str(no),))
       cur_data = c.fetchone()

       return template('edit_task', old=cur_data, no=no)

@app.route('/help')
def help():
    return static_file('help.html', root='.')

@app.error(403)
def mistake403(code):
	return 'There is a mistake in your url!'

@app.error(404)
def mistake404(code):
	return 'Sorry, this page does not exist!'

#app.install(plugins.WTForms())

debug(True)
run(app, reloader=True, port=5000)
