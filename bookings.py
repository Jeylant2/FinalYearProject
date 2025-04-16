import os
import sys
import cgi
import datetime
import sqlite3
from wsgiref.util import setup_testing_defaults, shift_path_info
from wsgiref.simple_server import make_server

DATABASE_FILEPATH="bookings.db"
def create_database():

    if os.path.exists(DATABASE_FILEPATH):
        os.remove(DATABASE_FILEPATH)
    
    
    db=sqlite3.connect(DATABASE_FILEPATH)
    q=db.cursor()
    
    sql=open("create.sql").read()
    statements=sql.split(";")
    for statement in statements:
        q.execute(statement)
        
    q.close
    db.commit()
    db.close()
    
def populate_database():
    db=sqlite3.connect(DATABASE_FILEPATH)
    q=db.cursor()
    
    sql="INSERT INTO users(id, name, number_plate) VALUES(?, ?, ?)"
    q.execute(sql, [1,"John Doe", "AB34CED"])
    q.execute(sql, [2,"Steve Doe", "EF56GEH"])
    q.execute(sql, [3,"Mac Doe", None])
    
    sql="INSERT INTO spaces(id, number, location) VALUES(?, ?, ?)"
    q.execute(sql, [1,1, "right space"])
    q.execute(sql, [2,2, "centre space"])
    q.execute(sql, [3,3, "left space"])

    sql= """
    INSERT INTO
        bookings
    (
        space_id, user_id, booked_on, booked_from, booked_to
    )
    VALUES(
        ?, ?, ?, ?, ?
    )"""
    
    q.execute(sql, [1, 1, '2025-04-04', '09:00', '10:00'])
    q.execute(sql, [3, 1, '2025-04-05', None, None])
    q.execute(sql, [2, 3, '2025-04-14', '12:00', None])
    q.execute(sql, [1, 2, '2025-04-04', '12:00', '13:00'])
    
    q.close()
    db.commit()
    db.close()
def select(sql_statement, params=None):
    if params is None:
        params=[]
    db=sqlite3.connect(DATABASE_FILEPATH)
    db.row_factory=sqlite3.Row
    q=db.cursor()
    try:
        q.execute(sql_statement, params)
        return q.fetchall()
    finally:
        q.close()
        db.close()
def execute(sql_statement, params=None):
    if params is None:
        params=[]
    db=sqlite3.connect(DATABASE_FILEPATH)
    q=db.cursor()
    try:
        q.execute(sql_statement, params)
        db.commit()
    finally:
        q.close()
        db.close()
        
def get_user(user_id):
    for user in select("SELECT * FROM users WHERE id=?",[user_id]):
        return user

def get_space(space_id):
    for space in select("SELECT * FROM spaces WHERE id=?",[space_id]):
        return space

def get_users():
    return select("SELECT * FROM users")

def get_spaces():
    return select("SELECT * FROM spaces")
def get_bookings():
    return select("SELECT * FROM v_bookings")
def get_bookings_for_user(user_id):    
    return select("SELECT * FROM v_bookings WHERE user_id = ?", [user_id])
def get_bookings_for_space(space_id):
    return select("SELECT * FROM v_bookings WHERE space_id= ?",[space_id])

def add_user_to_database(name,number_plate):
    execute(
        "INSERT INTO users(name, number_plate) VALUES (?, ?)",
        [name,number_plate]
    )
def add_space_to_database(number,location):
    execute(
        "INSERT INTO spaces(number,location) VALUES (?, ?)",
        [number, location]
    )
def add_booking_to_database(user_id, space_id, booked_on, booked_from=None, booked_to=None):
    execute(
        """
        INSERT INTO bookings(user_id, space_id, booked_on, booked_from, booked_to)
        VALUES(?, ?, ?, ?, ?)
        """,
        [user_id, space_id, booked_on, booked_from, booked_to]
    )    
def page(title, content):
    return """
    <html>
    <head>
    <title>ParkState Booking system: {title}</title>
    <style>
    body {{
        background-colour: #cff;
        margin:1em;
        padding:1em;
        border:thin solid black;
        font-family:sans-serif;
    }}
    td {{
        padding:0.5em;
        margin:0.5em;
        border:thin solid blue;
    }}
    </style>
    </head>
    <body>
    <h1>{title}</h1>
    {content}
    </body>
    </html>
    """.format(title=title, content=content)

def index_page(environ):
    html="""
    <ul>
        <li><a href="/users">Users</a></li>
        <li><a href="/spaces">Spaces</a></li>
        <li><a href="/bookings">Bookings</a></li>
    </ul>
    """
    return page("ParkState Booking system:",html)

def users_page(environ):
    html="<ul>"

    for user in get_users():
        html+='<li><a href="/bookings/user/{id}">{name}</a> ({number_plate})</li>\n'.format(
            id=user['id'],
            name=user['name'],
            number_plate=user['number_plate'] or "No numberplate"           
        )
    
    html+="</ul>"
    html+="<hr/>"
    html+="""<form method="POST" action="/add-user">
    <label for="name">Name:</label>&nbsp;<input type="text" name="name"/>
    <label for="number_plate">Number Plate:</label>&nbsp;<input type="text" name="number_plate"/>
    <input type="submit" name="submit" value="Add User"/>
    </form>"""
    return page("Users",html)


def spaces_page(environ):
    html="<ul>"
    
    for space in get_spaces():
        html+='<li><a href="/bookings/space/{id}">{number}</a> ({location})</li\n'.format(
            id=space['id'],
            number=space['number'],
            location=space['location'] or "invalid space"
        )
        
    html+="</ul>"
    html+="<hr/>"
    html+="""<form method="POST" action="/add-space">
    <label for="number">Parking Space Number:</label>&nbsp;<input type="text" name="number"/>
    <label for="location">Location:</label>&nbsp;<input type="text" name="location"/>
    <input type="submit" name="submit" value="Add Space"/>
    </form>"""
    return page("Spaces", html)
def all_bookings_page(environ):
    html="<table>"
    html+="<tr><td>User</td><td>Space</td>Date</td><td>Times</td></tr>"
    for booking in get_bookings():
        html+="<tr><td>{user_name}</td><td>{space_number}</td><td>{booked_on}</td><td>{booked_from}-{booked_to}</td></tr>".format(
            user_name=booking['user_name'],
            space_number=booking['space_number'],
            booked_on=booking['booked_on'],
            booked_from=booking['booked_from'] or "",
            booked_to=booking['booked_to'] or ""
        )
    html+="</table>"
        
    html+="<hr/>"
    html+='<form method="POST" action="/add-booking">'
    html+='<label for="user_id">User:</label>&nbsp;<select name="user_id">'
    for user in get_users():
        html+='<option value="{id}">{name}</option>'.format(**user)
    html+='</select>'
    html+='&nbsp;|&nbsp;'
    html+='<label for space_id">Space:</label>&nbsp;<select name="space_id">'
    for space in get_spaces():
        html+='<option value="{id}">{number}</option>'.format(**space)
    html+='</select>'
    html+='&nbsp;|&nbsp;'
    html+='<label for="booked_on">On</label>&nbsp;<input type="text" name="booked_on" value="{today}"/>'.format(today=datetime.date.today())
    html+='&nbsp;<label for="booked_from">between</label>&nbsp;<input type="text" name="booked_from"/>'
    html+='&nbsp;<label for="booked_to">and</label>&nbsp;<input type="text" name="booked_to"/>'
    html+='<input type="submit" name="submit" value="Add Booking"/></form>'
    return page("Bookings for %s" %user['name'], html)
def bookings_user_page(environ):
    user_id=int(shift_path_info(environ))
    user=get_user(user_id)
    html="<table>"
    html+="<tr><td>Space</td><td>Date</td><td>Times</td></tr>"
    for booking in get_bookings_for_user(user_id):
        html+="<tr><td>{space_number}</td><td>{booked_on}</td><td>{booked_from}-{booked_to}</td></tr>".format(
            space_number=booking['space_number'],
            booked_on=booking['booked_on'],
            booked_from=booking['booked_from'] or "",
            booked_to=booking['booked_to'] or ""
        )
    html+="</table>"
    html+="<hr/>"
    html+='<form method="POST" action="/add-booking">'
    html+='<input type="hidden" name="user_id" value="{user_id}"/>'.format(user_id=user_id)
    html+='<label for="space_id">Space:</label>&nbsp;<select name="space_id">'
    
    for space in get_spaces():
        html+='<option value="{id}">{number}</option>'.format(**space)
        html+='</select>'
        html+='&nbsp;|&nbsp;'
        html+='<label for="booked_on">On</label>&nbsp;<input type="text" name="booked_on" value="{today}"/>'.format(today=datetime.date.today())
        html+='&nbsp;<label for="booked_from">between</label>&nbsp;<input type="text" name="booked_from"/>'
        html+='&nbsp;<label for="booked_to">and</label>&nbsp;<input type="text" name="booked_to"/>'
        html+='<input type="submit" name="submit" value="Add Booking"/></form>'
        return page("Bookings for %s" % user['name'], html)

def bookings_space_page(environ):
    space_id=int(shift_path_info(environ))
    space=get_space(space_id)
    html="<table>"
    html+="<tr><td>User</td><td>Date</td><td>Times</td></tr>"
    for booking in get_bookings_for_space(space_id):
        html+="<tr><td>{user_name}</td><td>{booked_on}</td><td>{booked_from}-{booked_to}</td></tr>".format(
            user_name=booking['user_name'],
            booked_on=booking['booked_on'],
            booked_from=booking['booked_from'] or "",
            booked_to=booking['booked_to'] or ""
        )
    html+="</table>"
    html+="<hr/>"
    html+='<form method="POST" action="/add-booking">'
    html+='<input type="hidden" name="space_id" value="{space_id}"/>'.format(space_id=space_id)
    html+='<label for="user_id">User:</label>&nbsp;<select name="user_id">'
    
    for user in get_users():
        html+='<option value="{id}">{name}</option>'.format(**user)
    html+='</select>'
    html+='&nbsp;|&nbsp;'
    html+='<label for="booked_on">On</label>&nbsp;<input type="text" name="booked_on" value="{today}"/>'.format(today=datetime.date.today())
    html+='&nbsp;<label for="booked_from">between</label>&nbsp;<input type="text" name="booked_from" />'
    html+='&nbsp;<label for="booked_to">and</label>&nbsp;<input type="text" name="booked_to" />'
    html+='<input type="submit" name="submit" value="Add Booking"/></form>'
    return page("Bookings for parking space %s" % space['number'], html)

def bookings_page(environ):
    category=shift_path_info(environ)
    if not category:
        return all_bookings_page(environ)
    elif category=="user":
        return bookings_user_page(environ)
    elif category=="space":
        return bookings_space_page(environ)
    else:
        return "Error category"
def add_user(environ):
    form=cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ.copy(), keep_blank_values=True)
    add_user_to_database(form.getfirst("name"),form.getfirst('number_plate',""))
    print("New User Added to db")
def add_space(environ):
    form=cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ.copy(),keep_blank_values=True)
    add_space_to_database(form.getfirst("number"),form.getfirst('location', None))
    print("New Space Added to db")
def add_booking(environ):
     form=cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ.copy(), keep_blank_values=True)
     add_booking_to_database(
         form.getfirst("user_id"),
         form.getfirst("space_id"),
         form.getfirst("booked_on"),
         form.getfirst("booked_from"),
         form.getfirst("booked_to")
    )   
def webapp(environ, start_response):
    setup_testing_defaults(environ)
    status='200 OK'
    headers=[('Content-type', 'text/html; charset=utf-8')]
    
    param1=shift_path_info(environ)
    if param1=="":
        data=index_page(environ)
    elif param1== "users":
        data=users_page(environ)
    elif param1== "spaces":
        data=spaces_page(environ)
    elif param1=="bookings":
        data=bookings_page(environ)
    elif param1=="add-user":
        add_user(environ)
        print("User added")
        status="301 Redirect"
        headers.append(("Location","/users"))
        data=""
    elif param1=="add-space":
        add_space(environ)
        status="301 Redirect"
        headers.append(("Location","/spaces"))
        data=""
    elif param1=="add-booking":
         add_booking(environ)
         status="301 Redirect"
         headers.append(("Location", environ.get("HTTP_REFERER","/bookings")))
         data=""
    else:
        status='404 Not Found'
        data="Not Found: %s" % param1
        
    start_response(status, headers)
    return [data.encode("utf-8")]

def run_website():
    httpd=make_server('', 8000, webapp)
    print("serving on port 8000...")
    httpd.serve_forever()
    
if __name__=='__main__':
    print("About to create database %s" % DATABASE_FILEPATH)
    create_database()
    print("About to populate database %s" % DATABASE_FILEPATH)
    populate_database()
    print("About to run webserver")
    run_website()
    print("Finished")
    
