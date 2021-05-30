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
            print('Error: bad arguments.')
            return
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
        print('You do not have permission for this operation.')
        return
    if check_register_param(name, username, password, room, permission, serving) is False:
        return False
    encrypted_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    c.execute(f"SELECT * FROM employee WHERE username='{username}'")
    permissions = [int(i) for i in permission.split(',') if i.isdigit() is True]
    permissions = list(dict.fromkeys(permissions))
    if len(c.fetchall()) == 0:
        c.execute(f"INSERT INTO employee VALUES ('{name}', '{username}', '{encrypted_password.decode()}', {room},"
                  f" '{permissions}', {serving})")
        print(f'{name} registered successfully.')
    else:
        print('Error: Username already exist.')


def check_register_param(name, username, password, room, permission, serving):
    if name == '-1' or username == '-1' or password == '-1' or room == '-1' or permission == '-1':
        print('Employee registration canceled.')
        return False
    if name.replace(' ', '').isalpha() is False:
        print('The name must contain only letters.')
        return False
    if len(name) < 2:
        print('The length of the name must be greater than 1.')
        return False
    if username.find(' ') != -1 or username.find('\t') != -1:
        print('Username can\'t contain spaces.')
    if len(username) < 3:
        print('The length of the username must be greater than 2.')
        return False
    if len(password) < 3:
        print('The length of the password must be greater than 2.')
        return False
    if room.isdigit() is False:
        print('The room number must be a number.')
        return False
    if permission.replace(',', '').isdigit() is False:
        print('The permission must contain only commas and numbers.')
        return False
    try:
        int(serving)
    except ValueError:
        print('serving must be an integer.')
        return False
    return True


@conn_decorate
def remove_employee(c, username, employee_username):
    if check_permissions_and_user_exist(username, employee_username) is None:
        return
    c.execute(f"DELETE FROM employee WHERE username='{employee_username}'")
    print(f'Username {employee_username} removed successfully.')


@conn_decorate
def check_permissions_and_user_exist(c, username, employee_username):
    c.execute(f"SELECT permission FROM employee WHERE username='{username}'")
    if '3' not in c.fetchone()[0]:
        print('You do not have permission for this operation.')
        return None
    c.execute(f"SELECT permission FROM employee WHERE username='{employee_username}'")
    result = c.fetchone()
    if result is None:
        print(f'Username {employee_username} does not exist.')
        return None
    return result


@conn_decorate
def change_permission_to_employee(c, username, employee_username, permission):
    if permission.replace(',', '').isdigit() is False:
        print('The permission must contain only commas and numbers.')
        return
    old_permissions = check_permissions_and_user_exist(username, employee_username)
    if old_permissions is None:
        return
    permissions = list(dict.fromkeys([int(i) for i in permission.split(',') if i.isdigit() is True]))
    c.execute(f"UPDATE employee SET permission = '{permissions}' WHERE username = '{employee_username}'")
    print(f'{employee_username} new permissions: {permissions}')


@conn_decorate
def employee_list(c, username):
    result = check_permissions_and_user_exist(username, username)
    if result is None:
        return
    c.execute("SELECT name, username, room, permission, serving FROM employee")
    print(from_db_cursor(c))


@conn_decorate
def login(c, username, password):
    c.execute(f"SELECT password FROM employee WHERE username='{username}'")
    encrypted_password = c.fetchone()
    if encrypted_password is None:
        return False
    return bcrypt.checkpw(password.encode(), encrypted_password[0].encode())


@conn_decorate
def create_table(c):
    try:
        c.execute('CREATE TABLE employee (name text, username text, password text, room integer, permission text,'
                  ' serving integer)')
    except Exception as e:
        if e.__str__() == 'table employee already exists':
            pass
        else:
            raise e
