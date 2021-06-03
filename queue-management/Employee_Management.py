import sqlite3
import bcrypt
from prettytable import from_db_cursor


def conn_decorate(func):
    def wrapper(*args, **kwargs):
        if check_args(args) is True:
            conn = sqlite3.connect('yarin.db')
            c = conn.cursor()
            result = func(c, *args, **kwargs)
            conn.commit()
            conn.close()
            return result
        else:
            return 'Error: Incorrect arguments.'
    return wrapper


def check_args(args):
    """ check args to avoid sql injections"""
    for arg in args:
        if isinstance(arg, str) is True:
            if arg.find('\'') != -1 or arg.find('\"') != -1:
                return False
    return True


@conn_decorate
def register_employee(c, current_username, name, username, password, room, permission, serving):
    c.execute(f"SELECT permission FROM employee WHERE username='{current_username}'")
    if '3' not in c.fetchone()[0]:
        return 'You do not have permission for this operation.'

    error_msg = check_register_param(name, username, password, room, permission, serving)
    if error_msg != '':
        return error_msg
    encrypted_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    c.execute(f"SELECT * FROM employee WHERE username='{username}'")
    permissions = [int(i) for i in permission.split(',') if i.isdigit() is True]
    permissions = list(dict.fromkeys(permissions))
    if len(c.fetchall()) == 0:
        c.execute(f"INSERT INTO employee VALUES ('{name}', '{username}', '{encrypted_password.decode()}', {room},"
                  f" '{permissions}', {serving})")
        return f'{name} registered successfully.'
    else:
        return 'Error: Username already exist.'


def check_register_param(name, username, password, room, permission, serving):
    if name == '-1' or username == '-1' or password == '-1' or room == '-1' or permission == '-1':
        return 'Employee registration canceled.'
    if name.replace(' ', '').isalpha() is False:
        return 'The name must contain only letters.'
    if len(name) < 2:
        return 'The length of the name must be greater than 1.'
    if username.find(' ') != -1 or username.find('\t') != -1:
        return 'Username can\'t contain spaces.'
    if username.find('#') != -1:
        return 'Username can\'t contain \'#\'.'
    if len(username) < 3:
        return 'The length of the username must be greater than 2.'
    if len(password) < 3:
        return 'The length of the password must be greater than 2.'
    if password.find('#') != -1:
        return 'Password can\'t contain \'#\'.'
    if room.isdigit() is False:
        return 'The room number must be a number.'
    if permission.replace(',', '').isdigit() is False:
        return 'The permission must contain only commas and numbers.'
    try:
        int(serving)
    except ValueError:
        return 'serving must be an integer.'
    return ''


@conn_decorate
def remove_employee(c, username, employee_username):
    check_exist = check_permissions_and_user_exist(username, employee_username)
    if check_exist[1] == 'error':
        return check_exist[0]
    c.execute(f"DELETE FROM employee WHERE username='{employee_username}'")
    return f'Username {employee_username} removed successfully.'


@conn_decorate
def check_permissions_and_user_exist(c, username, employee_username):
    c.execute(f"SELECT permission FROM employee WHERE username='{username}'")
    if '3' not in c.fetchone()[0]:
        return 'You do not have permission for this operation.', 'error'
    c.execute(f"SELECT permission FROM employee WHERE username='{employee_username}'")
    result = c.fetchone()
    if result is None:
        return f'Username {employee_username} does not exist.', 'error'
    return result, ''


@conn_decorate
def change_permission_to_employee(c, username, employee_username, permission):
    if permission.replace(',', '').isdigit() is False:
        return 'The permission must contain only commas and numbers.'
    check_exist = check_permissions_and_user_exist(username, employee_username)
    if check_exist[1] == 'error':
        return check_exist[0]
    permissions = list(dict.fromkeys([int(i) for i in permission.split(',') if i.isdigit() is True]))
    c.execute(f"UPDATE employee SET permission = '{permissions}' WHERE username = '{employee_username}'")
    return f'{employee_username} new permissions: {permissions}'


@conn_decorate
def employee_list(c, username):
    check_exist = check_permissions_and_user_exist(username, username)
    if check_exist[1] == 'error':
        return check_exist[0]
    c.execute("SELECT name, username, room, permission, serving FROM employee")
    return from_db_cursor(c)


@conn_decorate
def login(c, username, password):
    c.execute(f"SELECT password FROM employee WHERE username='{username}'")
    encrypted_password = c.fetchone()
    if encrypted_password is None or username == '' or password == '':
        return False
    return bcrypt.checkpw(password.encode(), encrypted_password[0].encode())


@conn_decorate
def create_employee_table(c):
    try:
        c.execute('CREATE TABLE employee (name text, username text, password text, room integer, permission text,'
                  ' serving integer)')
    except Exception as e:
        if e.__str__() == 'table employee already exists':
            pass
        else:
            raise e
    try:
        c.execute('CREATE TABLE logged_in (username text, token text, logged_time text)')
    except Exception as e:
        if e.__str__() == 'table logged_in already exists':
            pass
        else:
            raise e
