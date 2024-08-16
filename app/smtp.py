#!/usr/bin/env python3
import logging
import smtplib
import yaml
import os
import inspect
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.logger import logger
logger = logging.getLogger('PSK_Rotator.smtp')
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)

class new():
    __version__ = "0.0.1"
    __author__  = "Tim Smith (tismith@extremenetworks.com)"

 #################################################################################################
    def __init__(self, yml_variables):
        self.yml_variables = yml_variables


    def send_message(self, body):
            # Build the email
            toHeader = ", ".join(self.yml_variables['email_list'])
            msg = MIMEMultipart()
            msg['Subject'] = self.yml_variables['email_sub']
            msg['From'] = self.yml_variables['smtp_sender_email']
            msg['To'] = toHeader
            msg.attach(MIMEText(body))
            try:
                server = smtplib.SMTP(self.yml_variables['smtp_server'], self.yml_variables['smtp_port'])
                server.starttls()
                server.login(self.yml_variables['smtp_username'],self.yml_variables['smtp_password'])
                server.send_message(msg)
                server.quit()
                #debug_print "email sent: %s" % fromaddr
            except Exception as e:
                    logmsg = "Something went wrong when sending the email to {}".format(self.yml_variables['smtp_sender_email'])
                    logger.error(logmsg)