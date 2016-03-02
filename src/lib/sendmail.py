import smtplib  
from email.mime.text import MIMEText  
mailto_list=["xchliu@bainainfo.com"]
#####################  
mail_host="smtp.163.com"
mail_user="dbreport"  
mail_pass="reportdb"  
mail_postfix="163.com"  
######################  
def send_mail(to_list,sub,content):  
    me=mail_user+"<"+mail_user+"@"+mail_postfix+">"  
    msg = MIMEText(content)  
    msg['Subject'] = sub  
    msg['From'] = me  
    msg['To'] = ";".join(to_list)  
   # msg['Content-type']=type
    try:  
        s = smtplib.SMTP(mail_host)  
        s.starttls()
        s.login(mail_user,mail_pass)  
        s.sendmail(me, to_list, msg.as_string())  
        #s.sendmail(me,to_list,content)
        s.close()  
        return True  
    except Exception, e:  
        print str(e)  
        return False  
if __name__ == '__main__':  
    if send_mail(mailto_list,"test","test"):  
        print "1"  
    else:  
        print "2"  