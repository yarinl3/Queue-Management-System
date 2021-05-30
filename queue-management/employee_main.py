from Queue_Managment import *
from Employee_Management import *
import os


def employee_main():
    create_table()
    username = input('\nUsername: ')
    password = input('Password: ')
    if login(username, password) is True:
        while choose_operation(username) != '-1':
            pass
    else:
        print('Username or password incorrect.')


def choose_operation(username):
    os.system('cls')
    print(f'Welcome {username}')
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
        next_customer(username)

    if operation_number == '2':
        number = input('Enter ticket number: ')
        pull_number(username, number)

    if operation_number == '3':
        termination_of_treatment(username)

    if operation_number == '4':
        return_to_queue(username)

    if operation_number == '5':
        ticket_number = input('Enter ticket number: ')
        remove_ticket(username, ticket_number)

    if operation_number == '6':
        print('Enter employee details or anytime enter -1 to cancel.')
        employee_name = input('Enter employee name: ')
        employee_username = input('Enter username: ')
        employee_password = input('Enter password: ')
        employee_room = input('Enter room number: ')
        employee_permissions = input('Enter permissions (numbers and commas): ')
        register_employee(username, employee_name, employee_username, employee_password, employee_room,
                          employee_permissions, -1)

    if operation_number == '7':
        employee_username = input('Enter username: ')
        if username == employee_username:
            print('You can\'t remove yourself.')
        else:
            remove_employee(username, employee_username)

    if operation_number == '8':
        employee_username = input('Enter username: ')
        employee_permissions = input('Enter permissions (numbers and commas): ')
        change_permission_to_employee(username, employee_username, employee_permissions)

    if operation_number == '9':
        employee_list(username)

    if operation_number not in [str(i) for i in range(1, 10)]+['-1']:
        print('bad operation number.')
    if operation_number != '-1':
        input('Press enter to continue')
    else:
        print('Goodbye')
    return operation_number
