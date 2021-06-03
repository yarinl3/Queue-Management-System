import sqlite3
import time


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
def take_number(c, department):
    number = next_number(department)
    if number is None:
        return f'Department {department} does not exist.'

    ticket_time = get_time()
    c.execute(f"INSERT INTO queue VALUES ({next_id()}, {number}, '{department}', '{ticket_time}', 'pending', -1)")
    return f"Number: {number}\nDepartment: {department}\ntime: {ticket_time}\n"


@conn_decorate
def check_number_exist(c, number):
    try:
        int(number)
    except ValueError:
        return f'{number} is not a number'
    c.execute(f"SELECT * FROM queue WHERE number={number}")
    if c.fetchone() is None:
        return f'Ticket number {number} does not exist.'
    return ''


@conn_decorate
def pull_number(c, username, number):
    number_exist_flag = check_number_exist(number)
    if number_exist_flag != '':
        return number_exist_flag
    number = int(number)
    check_permission_flag = check_permission(username, number)
    if check_permission_flag != '':
        return check_permission_flag
    termination_of_treatment(username)
    c.execute(f"UPDATE employee SET serving = {number} WHERE username = '{username}'")
    c.execute(f"SELECT room FROM employee WHERE username = '{username}'")
    room = c.fetchone()[0]
    c.execute(f"UPDATE queue SET status = 'in treatment', room = {room} WHERE number = {number}")
    return f'You are now handling {number}'


@conn_decorate
def remove_ticket(c, username, number):
    number_exist_flag = check_number_exist(number)
    if number_exist_flag != '':
        return number_exist_flag
    number = int(number)
    check_permission_flag = check_permission(username, number)
    if check_permission_flag != '':
        return check_permission_flag
    c.execute(f"SELECT room FROM queue WHERE number={number}")
    room = c.fetchone()[0]
    if room != -1:
        c.execute(f"UPDATE employee SET serving = -1 WHERE room = {room}")
    c.execute(f"DELETE FROM queue WHERE number={number}")
    return f'Ticket number {number} deleted successfully.'


@conn_decorate
def check_permission(c, username, number):
    c.execute(f"SELECT permission FROM employee WHERE username='{username}'")
    permissions = c.fetchone()[0]
    if (number <= 400 and '1' not in permissions) or (400 < number and '2' not in permissions):
        return 'You do not have permission for this operation.'
    return ''


@conn_decorate
def next_number(c, department):
    c.execute(f"SELECT number FROM queue WHERE department='{department}'")
    numbers = sorted([i[0] for i in c.fetchall()])
    return numbers[-1] + 1 if len(numbers) > 0 else first_number(department)


@conn_decorate
def next_customer(c, username):
    termination_of_treatment(username)
    c.execute(f"SELECT permission, room FROM employee WHERE username='{username}'")
    result = c.fetchone()
    permissions = result[0]
    room = result[1]
    number_range = (0, 0)
    if '1' in permissions and '2' in permissions:
        number_range = (100, 800)
    elif '1' in permissions:
        number_range = (100, 400)
    elif '2' in permissions:
        number_range = (400, 800)
    c.execute(f"SELECT ticket_id, number FROM queue WHERE number > {number_range[0]} AND number < {number_range[1]}")
    ticket_id_list = sorted([(i[0], i[1]) for i in c.fetchall()], key=lambda x: x[0])
    if len(ticket_id_list) > 0:
        c.execute(f"UPDATE queue SET status = 'in treatment', room = {room} WHERE ticket_id = {ticket_id_list[0][0]}")
        c.execute(f"UPDATE employee SET serving = {ticket_id_list[0][1]} WHERE username = '{username}'")
        return f'You are now handling {ticket_id_list[0][1]}'
    return None


@conn_decorate
def next_id(c):
    c.execute(f"SELECT ticket_id FROM queue")
    id_list = sorted([i[0] for i in c.fetchall()])
    return id_list[-1] + 1 if len(id_list) > 0 else 0


def first_number(department):
    if department == 'VAT Registration \\ Cancellation':
        return 101
    elif department == 'Collecting & Enforcing':
        return 201
    elif department == 'Autonomy Invoice':
        return 301
    elif department == 'Personal Password':
        return 401
    elif department == 'VAT Rebates':
        return 501
    elif department == 'Information Update':
        return 601
    elif department == 'Other':
        return 701
    return 701


def get_time():
    hours = str(time.localtime()[3]).zfill(2)
    minutes = str(time.localtime()[4]).zfill(2)
    seconds = str(time.localtime()[5]).zfill(2)
    return f'{hours}:{minutes}:{seconds}'


@conn_decorate
def return_to_queue(c, username):
    c.execute(f"SELECT serving FROM employee WHERE username='{username}'")
    ticket_number = c.fetchone()[0]
    c.execute(f"UPDATE queue SET status = 'pending', room = -1 WHERE number = {ticket_number}")
    c.execute(f"UPDATE employee SET serving = -1 WHERE username = '{username}'")
    return None


@conn_decorate
def termination_of_treatment(c, username):
    c.execute(f"SELECT serving FROM employee WHERE username='{username}'")
    ticket_number = c.fetchone()[0]
    c.execute(f"DELETE FROM queue WHERE number='{ticket_number}'")
    c.execute(f"UPDATE employee SET serving = -1 WHERE username = '{username}'")
    if ticket_number != -1:
        return f'Treatment for {ticket_number} was completed.'
    return None


@conn_decorate
def create_queue_table(c):
    try:
        c.execute('CREATE TABLE queue (ticket_id integer, number integer, department text, time text, status text,'
                  ' room integer)')
    except Exception as e:
        if e.__str__() == 'table queue already exists':
            pass
        else:
            raise e
