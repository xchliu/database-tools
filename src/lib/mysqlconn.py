# -*- coding:utf-8 -*-
"""
@author: xchliu

@file:  mysqlconn.py
"""

import logging
from src.setting import DBCONFIG

log = logging.getLogger('DBConnector')


try:
    import mysql.connector
except ImportError:
    log.error("Exceptions.ImportError: No module named mysql.connector")


class MysqlConn(object):
    """
        class of mysql connector
        all the sqls executed will be logged in debug mode

    """
    def __init__(self, conf=None, is_dict=True):
        """
            conf: dict of configuration
            DBCONFIG = {
                'host': '127.0.0.1',
                'port': 3306,
                'user': 'mega',
                'password': 'mega',
                'database': 'mega',
                'charset': 'utf8',
            }
        """
        self.db = DBCONFIG if not conf else conf
        self.is_dict = is_dict
        self.conn = None
        self.connect(self.db)

    def __del__(self):
        '''
            Close the connection when the object is going to erase
        '''
        self.close()

    def connect(self, conf={}):
        try:
            conn = mysql.connector.connect(**conf)
            if conn:
                self.conn = conn
            else:
                self.conn = None
            return conn
        except Exception, ex:
            msg = "Connect to {0} failed as :{1}".format(conf.get('host'), ex)
            log.error(msg)
            return False

    def cursor(self):
        '''
            The connection should be close if use the cursor out of this class
        '''
        if self.conn:
            return self.conn.cursor(dictionary=self.is_dict)
        else:
            return False

    def select(self, sql, size=0):
        '''
            Used for general queries that required
            Return list of dictionary of all the data as default
            Size:
                0 : all the matched rows
                1 : the first row default
                n : return n rows
                -1 : single value queried by sql ,return the value directly;
                    if none is returned by mysql server,return -1.
        '''
        log.debug(sql)
        if size == -1:
            self.is_dict = False
        cursor = self.cursor()
        if not cursor:
            if size != -1:
                return []
            else:
                return 0
        cursor.execute(sql)
        if size == 0:
            data = cursor.fetchall()
        elif size == 1:
            data = cursor.fetchone()
        elif size == -1:
            data = cursor.fetchone()
            data = data[0] if data else None
        else:
            data = cursor.fetchmany(size)
        if self.conn.unread_result:
            result = self.conn.get_rows()
        return data

    def dml(self, table, data, where=''):
        '''
            Insert data into table ,auto match the columns
        '''
        cursor = self.cursor()
        if not cursor:
            return False
        _columns = self.columns(table)
        if not _columns[0]:
            log.error('Failed to get table cloumns for {0},{1}'.format(table,_columns[1]))
            return False
        dataset = []
        #Filter the data,find the columns match the exist columns in table
        for d in data:
            row = {}
            for _d in d:
                if _d in _columns[1]:
                    row[_d] = d[_d]
            if row:
                dataset.append(row)
        if len(dataset) == 0:
            log.warn('No column matched when tring to insert table {0},\
                     columns are:{1}'.format(table, _columns[1]))
            return False
        #Execute the sql ,return insert id when action is insert ,
        #otherwise return the rows updated
        msg = ''
        for row in dataset:
            sqlArr = []
            for key in row.iterkeys():
                sqlArr.append("`{0}`=\"{1}\"".format(key, row[key]))
            if not where:
                sql = "insert into "+table +" set "+str.join(",", sqlArr)
                log.debug(sql)
                cursor.execute(sql)
                result = cursor.lastrowid
            else:
                sql = "update "+table +" set "+str.join(",", sqlArr)+" where "+where
                log.debug(sql)
                cursor.execute(sql)
                result = cursor.rowcount
            self.conn.commit()
            if not result:
                log.error(msg)
        return result

    def execute(self, sql):
        """
            Run sql directly
        """
        log.debug(sql)
        cursor = self.cursor()
        if cursor:
            try:
                cursor.execute(sql)
                self.conn.commit()
                return True
            except Exception as ex:
                log.error('Excute sql gets error:{}'.format(ex))
                log.error(sql)
        return False

    def columns(self, table):
        """
            Return a table's columns
        """
        try:
            sql = "select * from {} where 1=2".format(table)
            log.debug(sql)
            cursor = self.cursor()
            cursor.execute(sql)
            cursor.fetchall()
            columns = cursor.column_names
            log.debug(columns)
            return True, columns
        except Exception, ex:
            return False, ex

    def close(self):
        '''
            Close the connection
        '''
        if self.conn:
            self.conn.close()

class ConnPool(object):
    """docstring for ConnPool

    """
    def __init__(self, conf,):
        self.conf = conf

    def create_pool(self, name , size=1):
        self.connpool = mysql.connector.pooling.MySQLConnectionPool(
                                                    pool_name = name,
                                                    pool_size = size,
                                                    **self.conf)
        return self.connpool

    def add_connection(self, conn=None):
        self.connpool.add_connection(conn)

    def get_conection(self):
        return self.connpool.get_connection()


