"""
The preprocessor for SQL.

This makes it possible to maintain multiple dialects in one SQL statement. The
preprocessor language looks like the django template syntax, and for now only
supports {% dbif <dialect> %}<dialect specific SQL>{% enddbif %} where dialect
is one of 'monetdb' or 'postgresql'.
"""

import re

# \s*: match zero or more whitespaces
# {%% ifdb %(dialect)s %%}: match the tag, %(dialect)s should be set to dialect
# \n?: match zero or one newline
# (.*?): match any string in a non-greedy way and put it in a group
# {%% endifdb %%}: match the end tag
# \s*: match zero or more spaces
# \n?: match zero or one newline
ifdb_regexp = r'{%% ifdb %(dialect)s %%}\n?(.*?){%% endifdb %%}'


def filter_ifdb(string, dialect):
    """
    Filters out the {% ifdb ... %} statements in a string. The surrounding
    preprocess statement for the dialect are removed, for other dialects the
    complete statement is removed.

    :param string: the SQL string that may contain one or more ifdb statements
    :param dialect: the sql dialect you want to filter out
    :returns: the ifdb filtered string
    """
    # remove the condition around our dialect
    pattern = ifdb_regexp % {'dialect': dialect}
    step1 = re.sub(pattern, r'\1', string, flags=re.S | re.I)

    # remove the other dialects
    pattern = ifdb_regexp % {'dialect': r'\w+'}
    step2 = re.sub(pattern, '', step1, flags=re.S | re.I)

    return step2


def filter_tokens(string, tokens):
    """
    Replaces substrings of string.

    :param string: a SQL string
    :param tokens: a list of tupels of len 2 containing a mapping of what to
                   replace.
    :return: a token-replaced string
    """
    result = string
    for (token, replacer) in tokens:
        result = result.replace(token, replacer)
    return result


def dialectise(string, dialect, tokens=[]):
    """
    Preprocess a SQL string, removes or manipulates all preprocess statements.

    :param string: a string with possible SQL preprocessor content
    :param dialect: what SQL dialect do you want?
    :returns: a string containing only statements in the specified dialect
    """
    dialected = filter_ifdb(string, dialect)
    tokenized = filter_tokens(dialected, tokens)
    return tokenized
