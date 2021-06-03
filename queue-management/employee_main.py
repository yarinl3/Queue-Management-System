import os
import socket
import time
from protocol_parse import parse_to_protocol
from protocol_parse import parse_from_protocol
token = ''
username = ''


def employee_main():
    global token
    global username
    PORT = 5050
    SERVER = socket.gethostbyname(socket.gethostname())
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((SERVER, PORT))
    username = input('\nUsername: ')
    password = input('Password: ')
    result = send(my_socket, f"login('{username}', '{password}')")
    if result[0] == '#':
        token = result[1:]
        while choose_operation(my_socket) != '-1':
            pass
        send(my_socket, f"logout('{username}')")
    my_socket.close()


def send(my_socket, string):
    string = parse_to_protocol(string, token, username, is_client=True)
    if string is None:
        print('Error in send function: String is None.')
        return ''
    my_socket.send(string.encode())
    data = my_socket.recv(1024).decode()
    data = parse_from_protocol(data)
    if data != 'None' and data[0] != '#':
        print(data)
    return data


def choose_operation(my_socket):
    os.system('cls')
    print(f'Welcome {username}')
    print(f'Your token: {token}')
    print('\n1. Next customer\n'
          '2. Pull number from queue\n'
          '3. Termination of treatment\n'
          '4. Return number to queue\n'
          '5. Remove ticket by number\n'
          '6. Register employee\n'
          '7. Remove employee\n'
          '8. Change permission to employee\n'
          '9. Employee list\n'
          'For exit enter -1\n')

    operation_number = input('Enter operation number: ')
    if operation_number == '1':
        send(my_socket, f"next_customer('{username}')")

    if operation_number == '2':
        number = input('Enter ticket number: ')
        send(my_socket, f"pull_number('{username}', '{number}')")

    if operation_number == '3':
        send(my_socket, f"termination_of_treatment('{username}')")

    if operation_number == '4':
        send(my_socket, f"return_to_queue('{username}')")

    if operation_number == '5':
        ticket_number = input('Enter ticket number: ')
        send(my_socket, f"remove_ticket('{username}', '{ticket_number}')")

    if operation_number == '6':
        print('Enter employee details or anytime enter -1 to cancel.')
        employee_name = input('Enter employee name: ')
        employee_username = input('Enter username: ')
        employee_password = input('Enter password: ')
        employee_room = input('Enter room number: ')
        employee_permissions = input('Enter permissions (numbers and commas): ')
        send(my_socket, f"register_employee('{username}', '{employee_name}', '{employee_username}',"
                        f" '{employee_password}', '{employee_room}', '{employee_permissions}', -1)")

    if operation_number == '7':
        employee_username = input('Enter username: ')
        if username == employee_username:
            print('You can\'t remove yourself.')
        else:
            send(my_socket, f"remove_employee('{username}', '{employee_username}')")

    if operation_number == '8':
        employee_username = input('Enter username: ')
        employee_permissions = input('Enter permissions (numbers and commas): ')
        send(my_socket, f"change_permission_to_employee('{username}', '{employee_username}', '{employee_permissions}')")

    if operation_number == '9':
        send(my_socket, f"employee_list('{username}')")

    if operation_number not in [str(i) for i in range(1, 10)]+['-1']:
        print('bad operation number.')
    if operation_number != '-1':
        input('Press enter to continue')
        time.sleep(1)
    else:
        print('Goodbye')
    return operation_number
