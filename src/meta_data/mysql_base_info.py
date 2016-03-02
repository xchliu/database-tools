#coding:UTF8
##author xchliu 10-17 2012
##function: as a specified db server ,this tools check the basic infomation about the mysql server and log the conten into 
##          log file ,it could be used to know a db server at the first time or make anyone else wants to know the basic info
##          about the db mysql
##usage: python mysql_base_info.py /outputdir/ outputfile.txt  
##	     python mysql_base_info.py /outputdir                  --in this case,output file:/tmp/ 
import MySQLdb
import time
import getpass
import sys
db=["localhost","monitor","monitor",3306,"Undefined_Project"]
filename=""
class Sqls:
    """
    sqls for collect data,include variables and table data in information_schema
    """
    sql_list=["general"]
    sql_general=["show global variables like 'version%';","show global status like 'uptime';",
                 "show variables like '%character_set%';","show engines;"]
    sql_dir=["'%dir'", "'log_error'","'log_bin%'","'slow%'","'general%'"]  
    sql_deploy=["show slave status;","show slave hosts;"]
    sql_cluster="show variables like 'have_ndbcluster%'"
    sql_schema=["SELECT DISTINCT table_schema FROM `information_schema`.tables WHERE table_schema NOT IN('information_schema','performance_schema','`mysql`','test');",
                "SELECT COUNT(*) FROM `information_schema`.tables WHERE table_schema=%s",
                "SELECT COUNT(*) FROM `information_schema`.`TRIGGERS`",
                "SELECT COUNT(*) FROM `information_schema`.`ROUTINES`",
                "SELECT COUNT(*) FROM `information_schema`.`VIEWS`"
               ]
    sql_partition=["show variables like 'have_part%'",
                   "SELECT DISTINCT table_name,partition_method FROM `information_schema`.`PARTITIONS` WHERE partition_name IS NOT NULL"
                   ]
    sql_user="select user,host from mysql.user"
def db_config():
    """ config the db source by user，It will require user to input server infomation.
        returns:
            1  : config of db is available
            0 :  failed to config  
    """
    global db
    try:
        #print db
        host=raw_input("host:")
        if not host :
            db[0]="localhost"
        else:
            db[0]=host
        user=raw_input("user:")
        if not user:
            db[1]="root"
        else:
            db[1]=user
        port=raw_input("port:")
        if not port:
            db[3]=3306
        else:
            db[3]=port        
        db[2]=getpass.getpass(db[1]+"@"+db[0]+":"+str(db[3])+" password:")
        project=raw_input("project:")
        if not project:
            db[4]="UndefinedProject"
        else:
            db[4]=project
        #run a sql to check if  the server is able to connect
        cursor=db_conect()
        cursor.execute("select 1;")
        if cursor.fetchone()[0] == 1 :
            return 1
        else:
            return 0
    except Exception:
        return 0 
def db_conect():
    """
    connect to the db server and return the cursor or the exception
    """
    try:        
        conn=MySQLdb.connect(host=db[0],user=db[1],passwd=db[2],port=db[3])
        cursor=conn.cursor()
        return cursor
    except Exception,ex:
        print ex
def log(key="Default",value="Default",logtype=0):
    """log module 
    key : the item name to check
    value :  the value of check item
    """
    ### type: 1 title    0 content  3 formatel
    try:
        logfile=file(filename,'a')
        if logtype==1:
            logfile.write(value+"\n")
        elif logtype==0:
            string="%-35s:  %-10s"%(key,value)
            logfile.write(string+"\n")
        else:
            logfile.write("===============================\n")
    except Exception,ex:
        return ex
def merge_data():
    """
    main process to collect data using all the sqls in the class Sqls,call functions for each module
    """
    try:
        log(logtype=3) 
        for sql in Sqls.sql_general:
            get_data(sql)        
        for sql in Sqls.sql_dir:
            get_data("show variables like "+sql)
        deploy_data(Sqls.sql_deploy[0])
        schema_data(Sqls.sql_schema[0])
        part_data(Sqls.sql_partition[0])
        get_data(Sqls.sql_user)
    except Exception,ex:
        log(value=str(ex),logtype=1)
def schema_data(sql):
    """
    get the data for schema like table rows.
    """
    try:
        log(value="#counts of table for each db#",logtype=1)
        cursor=db_conect()
        cursor.execute(sql)
        result=cursor.fetchall()
        for db in result:
            cursor.execute(Sqls.sql_schema[1],db[0])
            table_count=cursor.fetchone()[0]
            log(db[0],table_count,0)
        log(value="============",logtype=1)
        cursor.execute(Sqls.sql_schema[3])
        result=cursor.fetchone()
        log("procedure_count",result[0],0)
        cursor.execute(Sqls.sql_schema[2])
        result=cursor.fetchone()
        log("trigger_count",result[0],0)
        cursor.execute(Sqls.sql_schema[4])
        result=cursor.fetchone()
        log("view_count",result[0],0)
        log(logtype=3)
    except Exception,ex:
        log(value=str(ex),logtype=1)
def part_data(sql):
    """ tracking data for prtion infomation"""
    try:
        cursor=db_conect()
        cursor.execute(sql)
        result=cursor.fetchone()
        log(result[0],result[1],0)
        if result[1]=="YES":
            log(value="#partion tables#",logtype=1)
            cursor.execute(Sqls.sql_partition[1])
            result=cursor.fetchall()
            for r in result:
                log(r[0],r[1],0)
        log(logtype=3)
    except Exception,ex:
        log(value=str(ex),logtype=1)         
def deploy_data(sql):    
    """deploy information"""
    try:
        cursor=db_conect()
        cursor.execute(sql)        
        result=cursor.fetchone()
        if not result or result == "" :
            log("is_slave","NO",0)            
        else:
            log("is_slave","YES",0) 
            log("master_host",result[1],0)
            log("master_port",result[3],0)
            log("io_stat",result[10],0)
            log("sql_stat",result[1],0)
            log("delay_time",result[30],0)
            log(value="============",logtype=1)
        cursor.execute(Sqls.sql_deploy[1])
        result=cursor.fetchall()
        if not result or result == "":
            log("is_master","NO",0)
        else:
            for r in result:
                log("slave_info",str(r[0])+str(r[1])+str(r[2])+str(r[3]))
        cursor.execute(Sqls.sql_cluster)
        result=cursor.fetchone()
        log(result[0],result[1],0)               
        log(logtype=3)
    except Exception,ex:
        log(value=str(ex),logtype=1)
def get_data(sql):
    """run the sql and log the result"""
    try:
        cursor=db_conect()
        cursor.execute(sql)        
        result=cursor.fetchall()
        for r in result:
            log(r[0],r[1],0)
        log(logtype=3)
    except Exception,ex:
        log(value=str(ex),logtype=1)
def main():
    """init the global config and lead the process"""    
    global filename,db
    file_folder=""   
    filename=time.strftime('%Y-%m-%d',time.localtime(time.time()))+"_"+sys.argv[2]
    if len(sys.argv) == 3:
        file_folder=sys.argv[1]
        filename=sys.argv[2]
        filename=file_folder+filename  
        #print filename 
        log("","MySQL Basic information on "+":"+str(db[3]),1)
        merge_data()        
        sys.exit()
    if len(sys.argv) == 2:
        file_folder=sys.argv[1]
        db_ping=db_config()
        if db_ping == 1:
            log("","MySQL Basic information on "+":"+str(db[3]),1)
            if  not file_folder:
                filename="/tmp/MysqlBaseinfo"+"_"+filename
            else:
                filename=file_folder+"MysqlBaseinfo"+"_"+filename 
            merge_data()
        else:
            sys.exit()
    print "output:"+filename
if __name__ == "__main__":
    main()