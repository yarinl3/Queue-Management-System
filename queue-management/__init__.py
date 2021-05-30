from customer_main import customer_main
from employee_main import employee_main
import sys


if __name__ == '__main__':
    args = sys.argv
    if len(args) == 1:
        print('Please enter argument.\n'
              '1 for customer main.\n'
              '2 for employee main.')
    elif len(args) > 2:
        print('Too many arguments.')
    else:
        if args[1] == '1':
            customer_main()
        elif args[1] == '2':
            employee_main()
        else:
            print('Bad argument\n'
                  '1 for customer main.\n'
                  '2 for employee main.')
