import socket
import re
import random
import time
from Queue_Managment import *
from Employee_Management import *
from protocol_parse import parse_to_protocol


def main():
    print('Starting...')
    try:
        start()
    except ConnectionRefusedError:
        print('Connection Error')


def start():
    get_bool = {'False': False, 'True': True}
    clear_tokens()
    PORT = 5050
    SERVER = socket.gethostbyname(socket.gethostname())
    ADDR = (SERVER, PORT)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    conn, addr = server.accept()
    create_queue_table()
    create_employee_table()
    username = ''
    while True:
        msg = conn.recv(1024).decode()
        if msg == '' or msg == 'None':
            print('Error: msg is Empty or None')
            break
        feedback, error_flag, login_flag, params = parsing(msg)
        if login_flag == 1:
            if get_bool[feedback] is True:
                feedback = f'#{get_token(username=params[0])}'
            else:
                feedback = 'Username or password incorrect.'
        feedback = parse_to_protocol(feedback, token='', username='', is_client=False)
        conn.send(feedback.encode())
        if error_flag == 1:
            print(feedback)
            break
    logout(username)
    conn.close()


def parsing(string):
    login_flag = 0
    params = []
    string, error_flag = check_token(string)
    if error_flag is True:
        return string, 1, login_flag, params
    if isinstance(string, str) is False or len(string) < 9:
        return "Improper structure: String length is less than 9 or string is not str", 1, login_flag, params

    module_number = string[0:3]
    func_number = string[3:6]
    number_of_params = string[6:9]
    if check_int(module_number, func_number, number_of_params) is False:
        return "Improper structure: Not positive int", 1, login_flag, params
    module_number = int(module_number)
    func_number = int(func_number)
    number_of_params = int(number_of_params)

    try:
        func_list[module_number][func_number][0].__name__
    except IndexError:
        return "Improper structure: The module or the function does not exist", 1, login_flag, params

    try:
        if number_of_params != func_list[module_number][func_number][1]:
            return "Improper structure: Number of parameters", 1, login_flag, params
    except IndexError:
        return "Improper structure: The module or the function does not exist", 1, login_flag, params

    if number_of_params == 0 and len(string) > 9:
        return "Improper structure: Number of parameters", 1, login_flag, params

    if number_of_params > 0:
        if len(string) > 9:
            params, error_flag = get_params(string[9:], number_of_params, func_list[module_number][func_number][2])

            if error_flag == 1:
                return params, 1, login_flag, params
        else:
            return "Improper structure: Number of parameters", 1, login_flag, params

    if module_number == 1 and func_number == 4:
        login_flag = 1

    return str(func_list[module_number][func_number][0](*params)), 0, login_flag, params


def get_params(params_string, number_of_params, classes):
    if len(params_string) % 30 != 0:
        return "Improper structure: The parameter length is not divisible by 30 with no remainder ", 1
    blocks = make_blocks(params_string, width=30)
    if len(blocks[-1]) != 30:
        return "Improper structure: The last block length is not 30", 1
    params = []
    parameter = ''
    next_serial = 1
    for block in blocks:
        if check_int(block[:3]) is False:
            return "Improper structure: Not positive int in parameters", 1
        serial = int(block[:3])
        if serial == 0 and parameter != '':
            params.append(parameter.strip())
            parameter = ''
            next_serial = 1
        if serial + 1 != next_serial:
            return "Improper structure: Incorrect parameters", 1
        parameter += block[3:]
        next_serial += 1
    if parameter != '':
        params.append(parameter.strip())
    if len(params) != number_of_params:
        return "Improper structure: Incorrect parameters", 1
    for i in range(len(classes)):
        if classes[i] == 'int':
            params[i] = int(params[i])
    return params, 0


def make_blocks(string, width):
    word = ''
    blocks = []
    for i in string:
        word += i
        if len(word) == width:
            blocks.append(word)
            word = ''
    if word != '':
        blocks.append(word)
    return blocks


def check_int(*args):
    for arg in args:
        try:
            if int(arg) < 0:
                return False
        except ValueError:
            return False
    return True


@conn_decorate
def get_token(c, username):
    string = ''
    for i in range(ord('A'), ord('Z')+1):
        char = chr(i)
        string += char
    for i in range(ord('a'), ord('z')+1):
        char = chr(i)
        string += char
    for i in range(ord('0'), ord('9')+1):
        char = chr(i)
        string += char
    token = ''.join(random.SystemRandom().choice(string) for _ in range(128))
    c.execute(f"INSERT INTO logged_in VALUES ('{username}', '{token}', '{time.time()}')")
    return token


@conn_decorate
def check_token(c, msg):
    # checks if its log in command or take number command
    if len(msg) >= 9 and (msg[:9] == '001004002' or msg[:9] == '000000001'):
        return msg, False
    if len(msg) > 0 and msg[0] == '#':
        list1 = msg.split('#')
        if len(list1) == 4:
            token = list1[1]
            username = list1[2]
            msg = list1[3]
            if check_args([token, username]) is True:
                c.execute(f"SELECT token FROM logged_in WHERE username='{username}'")
                user_token = c.fetchone()
                if user_token is not None:
                    user_token = user_token[0]
                    if user_token == token:
                        return msg, False
            else:
                return 'Error: Incorrect arguments (token, username).', True
    return 'Error: incorrect token.', True


@conn_decorate
def logout(c, username):
    if username != '':
        c.execute(f"DELETE FROM logged_in WHERE username='{username}'")
        return f'{username} logged out successfully.'
    return ''


@conn_decorate
def clear_tokens(c):
    c.execute(f"DELETE FROM logged_in")


func_list = [
            # Queue Management
            [(take_number, 1, ['str']), (pull_number, 2, ['str', 'str']),
             (remove_ticket, 2, ['str', 'str']), (check_permission, 2, ['str', 'int']), (next_customer, 1, ['str']),
             (return_to_queue, 1, ['str']), (termination_of_treatment, 1, ['str'])],
            # Employee Management
            [(register_employee, 7, ['str', 'str', 'str', 'str', 'str', 'str', 'int']),
             (remove_employee, 2, ['str', 'str']), (change_permission_to_employee, 3, ['str', 'str', 'str']),
             (employee_list, 1, ['str']), (login, 2, ['str', 'str']), (logout, 1, ['str'])]]


if __name__ == '__main__':
    main()
