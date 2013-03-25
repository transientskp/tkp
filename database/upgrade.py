#!/usr/bin/env python
"""
This script is used to upgrade or downgrade a TKP database to the latest or a specific revision. For this the
SQL files in sql/upgrade are used. Run this script directly from your shell, use -h or --help to get more info
on how to use it.
"""

import argparse
import os
import sys
import monetdb

sql_folder = os.path.join(os.path.dirname(__file__), 'sql/upgrade')

parser = argparse.ArgumentParser(description='Upgrade your TKP database.')
parser.add_argument('-d', '--database', help="what database to upgrade", default='trap', type=str)
parser.add_argument('-u', '--username', help="username for database", default='trap', type=str)
parser.add_argument('-p', '--password', help="password for database", default='trap', type=str)
parser.add_argument('-H', '--hostname', help="on what machine is the database running", default='localhost', type=str)
parser.add_argument('-P', '--port', help="on what port is the database running", default=50000, type=int)

def get_upgrades():
    """ Returns nested list of available upgrade paths"""
    files = [x for x in os.listdir(sql_folder) if x.endswith('.sql')]
    versions =  [(x[:-4].split('_to_')) for x in files]
    return [tuple(int(j) for j in i) for i in versions]

def get_version(cursor):
    """ returns version of current database schema"""
    cursor.execute("SELECT value FROM version WHERE name='revision'")
    return cursor.fetchall()[0][0]

def get_latest(current, upgrades):
    """return latest version reachable from current version"""
    latest = current
    while True:
        options = [to for from_,to in upgrades if from_ == latest and to > latest]
        if options:
            choice = max(options)
            latest = choice
        else:
            break
    return latest

def get_path(current, target, upgrades):
    """returns list of tuples which represents the upgrade path from 'current' to 'target'"""
    cursor = current
    steps = []
    if current < target:
        head = max
        cmp = lambda a,b: a<b
    elif current > target:
        head = min
        cmp = lambda a,b: a>b
    else:
        return []
    while True:
        options = [to for from_,to in upgrades if from_ == cursor and cmp(cursor, to) and cmp(cursor, target)]
        if options:
            choice = head(options)
            steps.append((cursor, choice))
            cursor = choice
        else:
            break
    return steps

def construct_sql(steps):
    """returns a string which is a list of concatenated SQL statements"""
    strings = []
    for step in steps:
        with open(os.path.join(sql_folder, '%s_to_%s.sql' % step), 'r') as f:
            for line in f.readlines():
                strings.append(line)
    return "".join(strings)

def ask_version(version):
    """ interact with user to determine what to do"""
    upgrades = get_upgrades()
    latest = get_latest(version, upgrades)
    answer = False
    if latest > version:
        msg = "a new version (%s) is available. You have %s. Upgrade?" % (latest, version)
        answer = True if raw_input("%s (y/N) " % msg).lower() == 'y' else False
        if answer:
            path = get_path(version, latest, upgrades)
    else:
        print "you already have the latest revision (%s)" % latest

    if version == latest or not answer:
        while True:
            msg = "do you want to up/down grade to a different revision? If so, which version?"
            answer = raw_input("%s (rev no) " % msg)
            if not answer.isdigit():
                print "please enter a version NUMBER"
                continue
            answer = int(answer)
            path = get_path(version, answer, upgrades)
            break
    return path

def main():
    args = vars(parser.parse_args())
    database = args['database']
    username = args['username']
    password = args['password']
    hostname = args['hostname']
    port = args['port']

    connection = monetdb.sql.connect(database=database, username=username, password=password, hostname=hostname, port=port)
    connection.set_autocommit(False)
    cursor = connection.cursor()
    version = get_version(cursor)
    path = ask_version(version)
    if not path:
        print "no upgrade path found"
        sys.exit(2)

    query = construct_sql(path)
    print query

    msg = "continue with upgrade?"
    answer = True if raw_input("%s (y/N) " % msg).lower() == 'y' else False
    if answer:
        for statement in query.split("%SPLIT%"):
#            print "Executing:"
#            print statement
            cursor.execute(statement)
#            raw_input('Done... continue?')
        connection.commit()
        print "Upgrade completed"
    else:
        print "upgrade cancelled"
        sys.exit(2)

if __name__ == "__main__":
    main()
