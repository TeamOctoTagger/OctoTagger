import re


REG_TAG = r'[a-z]+'
REG_OP = r'=|-|/'
REG_GROUP = r'\(|\)'
REG_NUM = r'\d+(\.\.\d+)?'


def parse(string):
    """
    Order of operations

    ()
        Group

    =
        Numeric Match

    -
        Not

    " "
        And

    /
        Or
    """

    def identity(scanner, token):
        return token

    def unknown(scanner, token):
        raise ValueError("Unknown token", token)

    scanner = re.Scanner([
        (REG_TAG, identity),
        (REG_OP, identity),
        (REG_GROUP, identity),
        (REG_NUM, identity),
        (r'\s+', None),
        (r'.', unknown),
    ])

    tokens = scanner.scan(string)[0]

    if tokens.count('(') != tokens.count(')'):
        raise ValueError('Unbalanced parentheses')

    def parse_group(tokens):
        result = []
        try:
            while True:
                token = tokens.next()
                if token == '(':
                    result.append(parse_group(tokens))
                elif token == ')':
                    return result
                else:
                    result.append(token)
        except StopIteration:
            return result

    def parse_numeric(tokens):
        result = []
        try:
            while True:
                token = tokens.next()
                if token == '=':
                    if not re.match(REG_TAG, result[-1]):
                        raise ValueError(
                            "Expected tag before `='",
                            result[-1]
                        )
                    number = tokens.next()
                    if not re.match(REG_NUM, number):
                        raise ValueError(
                            "Expected number after `='",
                            number
                        )
                    if '..' in number:
                        [lower, upper] = number.split('..')
                        result[-1] += ' BETWEEN ' + lower + ' AND ' + upper
                    else:
                        result[-1] += ' = ' + number
                else:
                    result.append(token)
        except StopIteration:
            return result

    def parse_not(tokens):
        result = []
        try:
            while True:
                token = tokens.next()
                if token == '-':
                    tag = tokens.next()
                    if not re.match(REG_TAG, tag):
                        raise ValueError("Expected tag after `-'", tag)
                    result.append('NOT (' + tag + ')')
                else:
                    result.append(token)
        except StopIteration:
            return result

    tokens = parse_numeric(iter(tokens))  # group 3 num tokens to 1
    tokens = parse_not(iter(tokens))  # group a not token to the tag token
    tokens = parse_group(iter(tokens))  # convert groups to sublists

    # TODO implement OR

    return tokens

if __name__ == '__main__':
    print(parse("alpha bear / -sun (cloud=2 / -cloud=1..3)"))
