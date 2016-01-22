import re


REG_TAG_NAME = r'[a-zA-Z][a-zA-Z0-9_]+'
REG_TAG_ID = r'[0-9]+'
REG_TAG = r'({}|{})'.format(REG_TAG_NAME, REG_TAG_ID)
REG_OP = r'(=|-|/)'
REG_GROUP = r'(\(|\))'
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
        (REG_NUM, identity),
        (REG_TAG, identity),
        (REG_OP, identity),
        (REG_GROUP, identity),
        (r'\s+', None),
        (r'', unknown),
    ])

    tokens = scanner.scan(string)[0]

    if tokens.count('(') != tokens.count(')'):
        raise ValueError('Unbalanced parentheses')

    def query_matching_files(match):
        parts = match.split("=")

        if re.match(reg_full(REG_TAG_NAME), parts[0]):
            clause = 'name = "{}"'.format(parts[0])
        elif re.match(reg_full(REG_TAG_ID), parts[0]):
            clause = 'pk_id = {}'.format(parts[0])
        else:
            raise ValueError("Found invalid tag specifier", parts[0])

        if len(parts) > 2:
            raise ValueError("Found too many `='", match)
        elif len(parts) == 2:
            if '..' in parts[1]:
                [lower, upper] = parts[1].split('..')
                clause += ' AND amount BETWEEN {} AND {}'.format(lower, upper)
            else:
                clause += ' AND amount = {}'.format(parts[1])

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
                    if len(result) == 0:
                        raise ValueError("Expected tag before `='")
                    elif not re.match(reg_full(REG_TAG), result[-1]):
                        raise ValueError(
                            "Expected tag before `='",
                            result[-1]
                        )

                    try:
                        number = tokens.next()
                    except StopIteration:
                        raise ValueError("Expected something after `='")

                    if not re.match(reg_full(REG_NUM), number):
                        raise ValueError(
                            "Expected number after `='",
                            number
                        )
                    result[-1] += '=' + number  # group the tokens
                elif '..' in token:
                    raise ValueError("An amount requires a tag")
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
