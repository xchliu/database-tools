#coding:UTF8
##author xchliu 10-17 2012 
##usage: python mysql_base_info.py outputfile.txt  
##	     python mysql_base_info.py                  --in this case,output file:/tmp/ 
import MySQLdb,time,getpass,sys
db=["localhost","backup","backup",3306,"Undefined_Project"]
filename=""
class sqls:
    sql_list=["general",]
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
    """ config the db source by user
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
        cursor=db_conect()
        cursor.execute("select 1;")
        if cursor.fetchone()[0] == 1 :
            return 1
        else:
            return 0
    except Exception:
        return 0 
def db_conect():
    try:        
        conn=MySQLdb.connect(host=db[0],user=db[1],passwd=db[2],port=db[3])
        cursor=conn.cursor()
        return cursor
    except Exception,ex:
        print ex
def log(key="Default",value="Default",logtype=0):
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
    try:
        log(logtype=3) 
        for sql in sqls.sql_general:
            get_data(sql)        
        for sql in sqls.sql_dir:
            get_data("show variables like "+sql)
        deploy_data(sqls.sql_deploy[0])
        schema_data(sqls.sql_schema[0])
        part_data(sqls.sql_partition[0])
        get_data(sqls.sql_user)
    except Exception,ex:
        log(value=str(ex),logtype=1)
def schema_data(sql):
    try:
        log(value="#counts of table for each db#",logtype=1)
        cursor=db_conect()
        cursor.execute(sql)
        result=cursor.fetchall()
        for db in result:
            cursor.execute(sqls.sql_schema[1],db[0])
            table_count=cursor.fetchone()[0]
            log(db[0],table_count,0)
        log(value="============",logtype=1)
        cursor.execute(sqls.sql_schema[3])
        result=cursor.fetchone()
        log("procedure_count",result[0],0)
        cursor.execute(sqls.sql_schema[2])
        result=cursor.fetchone()
        log("trigger_count",result[0],0)
        cursor.execute(sqls.sql_schema[4])
        result=cursor.fetchone()
        log("view_count",result[0],0)
        log(logtype=3)
    except Exception,ex:
        log(value=str(ex),logtype=1)
def part_data(sql):
    try:
        cursor=db_conect()
        cursor.execute(sql)
        result=cursor.fetchone()
        log(result[0],result[1],0)
        if result[1]=="YES":
            log(value="#partion tables#",logtype=1)
            cursor.execute(sqls.sql_partition[1])
            result=cursor.fetchall()
            for r in result:
                log(r[0],r[1],0)
        log(logtype=3)
    except Exception,ex:
        log(value=str(ex),logtype=1)         
def deploy_data(sql):    
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
        cursor.execute(sqls.sql_deploy[1])
        result=cursor.fetchall()
        if not result or result == "":
            log("is_master","NO",0)
        else:
            for r in result:
                log("slave_info",r[0]+r[1]+r[2]+r[3])
        cursor.execute(sqls.sql_cluster)
        result=cursor.fetchone()
        log(result[0],result[1],0)               
        log(logtype=3)
    except Exception,ex:
        log(value=str(ex),logtype=1)
def get_data(sql):
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
    global filename,db
    file_folder=""   
    if len(sys.argv) == 3:
        file_folder=sys.argv[1]        
    filename=time.strftime('%Y-%m-%d',time.localtime(time.time()))+"_"+sys.argv[2]
    if  not file_folder:
        filename="/tmp/MysqlBaseinfo_"+db[0]+"_"+filename
    else:
        filename=file_folder+"MysqlBaseinfo_"+"_"+filename
    if len(sys.argv) == 4:
        db_ping=db_config()
        if db_ping == 1:
            log("","MySQL Basic information on "+":"+str(db[3]),1)
            merge_data()
        else:
            sys.exit()
    else:
        log("","MySQL Basic information on "+":"+str(db[3]),1)
        merge_data()
    print "output:"+filename
if __name__ == "__main__":
    main()



