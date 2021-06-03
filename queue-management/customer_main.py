import socket
from protocol_parse import parse_to_protocol
from protocol_parse import parse_from_protocol


def customer_main():
    PORT = 5050
    SERVER = socket.gethostbyname(socket.gethostname())
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((SERVER, PORT))

    print('Welcome to VAT office')
    id_number = input('Please enter ID number:\n')
    while check_id(id_number) is False:
        id_number = input('\nThe ID number is wrong. Please try again:\n')
    print('Choose department and enter its number:\n'
          '1. VAT Registration \\ Cancellation\n'
          '2. Collecting & Enforcing\n'
          '3. Autonomy Invoice\n'
          '4. Information Update\n'
          '5. Personal Password\n'
          '6. VAT Rebates\n'
          '7. Other\n')
    try:
        option = int(input())
    except ValueError:
        print('Your option must be number.')
        my_socket.close()
        return
    send(my_socket, f"take_number('{department_by_number(option)}')")
    my_socket.close()


def send(my_socket, string):
    string = parse_to_protocol(string, token='', username='', is_client=True)
    if string is None:
        print('Error in send function: String is None.')
        return ''
    my_socket.send(string.encode())
    data = my_socket.recv(1024).decode()
    data = parse_from_protocol(data)
    print(data)


def check_id(number):
    if len(number) > 9 or number.isdigit() is False:
        return False
    number = number.zfill(9)
    number_sum = 0
    for i in range(9):
        if i % 2 == 1:
            mult = int(number[i]) * 2
            if mult > 9:
                number_sum += mult // 10 + mult % 10
            else:
                number_sum += mult
        else:
            number_sum += int(number[i])
    if number_sum % 10 != 0:
        return False
    return True


def department_by_number(option):
    options = {1: 'VAT Registration \\ Cancellation', 2: 'Collecting & Enforcing', 3: 'Autonomy Invoice',
               4: 'Information Update', 5: 'Personal Password', 6: 'VAT Rebates', 7: 'Other'}
    if 0 < option < 8:
        return options[option]
    else:
        return 'Other'
