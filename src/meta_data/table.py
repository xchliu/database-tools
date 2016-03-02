#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Author : xchliu
    Date   : 3/2/16
    
"""
from src.lib.mysqlconn import MysqlConn

class Column(object):
    """

    """
    def __init__(self, column=dict()):

        self.field = column.get('Field')
        self.type = column.get('Type')
        self.collation = column.get('Collation')
        self.isnull = column.get('Null')
        self.key = column.get('Key')
        self.extra = column.get('Extra')
        self.privileges = column.get('Privileges')
        self.comment = column.get('Comment')


class Table(object):
    """

    """
    def __init__(self, schema, name):
        self.columns = [Column(c) for c in  columns(schema, name)]


def columns(schema, table_name):
    q = MysqlConn()
    sql = 'show full columns from %s from %s' % (table_name, schema)
    data = q.select(sql)
    return data



def main():
    print columns('mega', 'report_weekly')
    return


if __name__ == "__main__":
    main()