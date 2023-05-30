"""
The preprocessor for SQL.

This makes it possible to maintain multiple dialects in one SQL statement. The template is
preprocessed by Jinja, expecting a variable `db` to be set with properties `engine` and
`version`.
"""

from jinja2 import Environment

env = Environment()


def dialectise(string, dialect, tokens=[], version=None):
    """
    Preprocess a SQL string, removes or manipulates all preprocess statements.

    :param string: a string with possible SQL preprocessor content
    :param dialect: what SQL dialect do you want?
    :returns: a string containing only statements in the specified dialect
    """
    template = env.from_string(string)
    return template.render(db={"engine": dialect, "version": version})

