import sqlite3
from bottle import route, run, debug, template, request, static_file, error

# only needed when you run Bottle on mod_wsgi
#from bottle import default_app

@route('/todo')
def todo_list():

    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("select id, task from todo where status like '1'")
    result = c.fetchall()
    c.close()

    output = template('make_table', rows=result)
    return output

@route('/new', method='GET')
def new_item():

    if request.GET.save:

        new = request.GET.task.strip()
        conn = sqlite3.connect('todo.db')

        c = conn.cursor()
        c.execute("insert into todo (task, status) values (?, ?)", (new, 1))
        new_id = c.lastrowid

        conn.commit()
        c.close()

        return '<p>The new task was inserted into the database, the ID is %s</p>'
    
    else:
        return template('new_task.tpl')

#@route('/item<item:re:[0-9]+>')
@route('/item/<item:re:[0-9]+>')
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

@route('/edit/<no:int>', mehtod='GET')
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

@route('/help')
def help():
    return static_file('help.html', root='.')

@error(403)
def mistake403(code):
	return 'There is a mistake in your url!'

@error(404)
def mistake404(code):
	return 'Sorry, this page does not exist!'

debug(True)
run(reloader=True, port=5000)
