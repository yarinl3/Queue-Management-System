from Queue_Managment import *


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
    options = {1: 'VAT Registration \\ Cancellation', 2: 'Collecting & Enforcing', 3: 'Information Update',
               4: 'Autonomy Invoice', 5: 'Personal Password', 6: 'VAT Rebates', 7: 'Other'}
    if 0 < option < 8:
        return options[option]
    else:
        return 'Other'


def customer_main():
    print('Welcome to VAT office')
    id_number = input('Please enter ID number:\n')
    while check_id(id_number) is False:
        id_number = input('\nThe ID number is wrong. Please try again:\n')
    create_table()
    print('Choose department and enter its number:\n'
          '1. VAT Registration \\ Cancellation\n'
          '2. Collecting & Enforcing\n'
          '3. Information Update\n'
          '4. Autonomy Invoice\n'
          '5. Personal Password\n'
          '6. VAT Rebates\n'
          '7. Other\n')
    try:
        option = int(input())
    except ValueError:
        print('Your option must be number.')
        return
    take_number(department_by_number(option))
