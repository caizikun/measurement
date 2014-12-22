from instrument import Instrument
import types
import smtplib
from email.mime.text import MIMEText
from threading import Thread

class send_email(Instrument):
    '''This instrument sends an email using a 
	gmall account defined by the (username,password) parameters'''
	
	
    def __init__(self, name, username='not_set', password='not_set', use_threading = False):
        Instrument.__init__(self,name)

        self.add_parameter('username',
                type=types.StringType,
                flags=Instrument.FLAG_GETSET)
        self.add_parameter('password',
                type=types.StringType,
                flags=Instrument.FLAG_GETSET)				

        self._username = username
        self._password = password

        self.add_function("send_email")
		
        self._host='smtp.gmail.com:587'
        self._mail_append='@googlemail.com'
        self._use_threading = use_threading
		
    def do_get_username(self):
        return self._username

    def do_set_username(self, username):
        self._username = username

    def do_get_password(self):
        return self._password

    def do_set_password(self, password):
        self._password = password

    def send_email(self,recipients,subject,message):
        '''Sends an email to 'recipients' (string or list of strings), with subject and message'''
        if isinstance(recipients,str):recipients=[recipients]
        sender=self._username + self._mail_append
        try:
            for recipient in recipients:
                if self._use_threading:
                    t = Thread(target = _actually_send, args=(self._host,self._username,self._password,sender,recipient,subject,message))
                    t.start()
                else:
                    _actually_send(self._host,self._username,self._password,sender,recipient,subject,message)
        except smtplib.SMTPException as mailerror:
            print "Mailing error:", mailerror
            return False
        return True
	
def _actually_send(host,username,password,sender,recipient,subject,message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    server = smtplib.SMTP(host)  
    server.starttls()  
    server.login(username,password)  
    server.sendmail(sender, recipient, msg.as_string())  
    server.quit()

