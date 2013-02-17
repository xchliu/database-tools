from libs import sendmail
import MySQLdb

class Repl_Monitor():
    def __init__(self,port=3306,host='127.0.0.1'):
        self.port=port
        self.host=host
        self.sql='show slave status'
    def replicat_monitor(self):
        try:
            conn = MySQLdb.Connect(host=self.host,user='monitor',passwd='monitor',port=self.port)
            cursor = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
            cursor.execute(self.sql)
            data = cursor.fetchall()
            if len(data) > 0 :
                data=data[0]
                IO = data.get("Slave_IO_Running")
                SQL = data.get("Slave_SQL_Running")
                relay = data.get("Seconds_Behind_Master")
                IO_error = data.get("Last_IO_Error")
                SQL_error =  data.get("Last_SQL_Error")
                if not isinstance(relay,int):
                    relay=-1
                if IO != "Yes" or SQL != "Yes" or relay > 10000:
                    print "Slave_IO_Running : "+IO
                    print "Slave_SQL_Running : " + SQL
                    print "Seconds_Behind_Master :" + str(relay)
                    print "Last_IO_Error : "+ IO_error
                    print "Last_SQL_Error :" + SQL_error
                else:
                    print 1
            else:
                print "NULL"
            cursor.close()
            conn.close()
        except Exception, ex:
            print ex
if __name__ == "__main__":
    R=Repl_Monitor()
    R.replicat_monitor()