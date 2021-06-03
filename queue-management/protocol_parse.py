import re
func_dict = {'take_number': '000000001', 'pull_number': '000001002', 'remove_ticket': '000002002',
             'check_permission': '000003002', 'next_customer': '000004001', 'return_to_queue': '000005001',
             'termination_of_treatment': '000006001', 'register_employee': '001000007', 'remove_employee': '001001002',
             'change_permission_to_employee': '001002003', 'employee_list': '001003001', 'login': '001004002',
             'logout': '001005001'}


def parse_to_protocol(string, token, username, is_client):
    # noinspection PyBroadException
    try:
        new_string = ''
        if is_client is True:
            func = re.search('^.*\(', string).group()[:-1]
            args = eval(re.search('\(.*\)', string).group()[1:-1])
            new_string += func_dict[func]
            if isinstance(args, str) is True:
                # solve the problem that tuple of one string become string
                args = [args]
            for arg in args:
                new_string += make_blocks_to_protocol(arg)
            if func != 'login' and func != 'take_number' and is_client:
                new_string = f'#{token}#{username}#' + new_string
        else:
            new_string += make_blocks_to_protocol(string)
        return new_string
    except Exception:
        print('Error while parsing string to protocol.')


def parse_from_protocol(string):
    # there's only one parameter
    if len(string) % 30 != 0:
        return "Improper structure: The parameter length is not divisible by 30 with no remainder "
    blocks = make_blocks_from_protocol(string, width=30)
    if len(blocks[-1]) != 30:
        return "Improper structure: The last block length is not 30"
    parameter = ''

    for block in blocks:
        parameter += block[3:]
    return parameter.strip()


def make_blocks_from_protocol(string, width):
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


def make_blocks_to_protocol(arg):
    string = ''
    word = ''
    words = []
    word_index = 0
    arg = str(arg)
    for i in arg:
        word += i
        if len(word) == 27:
            words.append(str(word_index).zfill(3) + word)
            word_index += 1
            word = ''
    if word != '':
        words.append(str(word_index).zfill(3) + word.ljust(27))
    for i in words:
        string += i
    return string
