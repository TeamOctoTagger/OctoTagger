import re


REG_TAG = r'[a-z]+'
REG_OP = r'=|-|/'
REG_GROUP = r'\(|\)'
REG_NUM = r'\d+(\.\.\d+)?'
REG_TAG_MATCH = r'{}(={})?'.format(REG_TAG, REG_NUM)


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

    def query_matching_files(match):
        if '=' in match:
            [tag, number] = match.split('=')
            clause = 'name = "{}"'.format(tag)
            if '..' in match:
                [lower, upper] = number.split('..')
                clause += ' AND amount BETWEEN {} AND {}'.format(lower, upper)
            else:
                clause += ' AND amount = {}'.format(number)
        else:
            clause = 'name = "{}"'.format(match)

        return (
            "file.pk_id IN ("
            "SELECT pk_fk_file_id FROM file_has_tag"
            " LEFT JOIN tag ON pk_fk_tag_id = pk_id"
            " WHERE " + clause + ")"
        )

    def reg_full(reg):
        return '^' + reg + '$'

    def parse_numeric(tokens):
        result = []
        try:
            while True:
                token = tokens.next()
                if token == '=':
                    if not re.match(reg_full(REG_TAG), result[-1]):
                        raise ValueError(
                            "Expected tag before `='",
                            result[-1]
                        )
                    number = tokens.next()
                    if not re.match(reg_full(REG_NUM), number):
                        raise ValueError(
                            "Expected number after `='",
                            number
                        )
                    result[-1] += '=' + number  # group the tokens
                else:
                    result.append(token)
        except StopIteration:
            return result

    def parse_tag(tokens):
        result = []
        try:
            while True:
                token = tokens.next()
                if re.match(reg_full(REG_TAG_MATCH), token):
                    result.append(query_matching_files(token))
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
                    if not re.match(r'file\.pk_id', tag):
                        raise ValueError("Expected tag query after `-'", tag)
                    result.append('NOT (' + tag + ')')
                else:
                    result.append(token)
        except StopIteration:
            return result

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

    def parse_or(tokens):
        if tokens[0] == '/' or tokens[-1] == '/':
            raise ValueError("Found OR on edge")

        result = ""
        left = []
        for token in tokens:
            if token == '/':
                result += '(' + ' AND '.join(left) + ')'
                result += ' OR '
                left = []
            elif type(token) == list:
                left.append(parse_or(token))
            else:
                left.append(token)

        result += '(' + ' AND '.join(left) + ')'
        result = '(' + result + ')'
        return result

    tokens = parse_numeric(iter(tokens))  # group 3 num tokens to 1 token
    tokens = parse_tag(iter(tokens))  # convert tag to query
    tokens = parse_not(iter(tokens))  # group a not token to the tag query
    tokens = parse_group(iter(tokens))  # convert groups to sublists
    query = parse_or(tokens)

    return query

if __name__ == '__main__':
    print(parse("alpha bear / -sun (cloud=2 / -cloud=1..3)"))
