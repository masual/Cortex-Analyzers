#!/usr/bin/env python
# encoding: utf-8

from cortexutils.responder import Responder
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json

class AuthMailer(Responder):
    def __init__(self):
        Responder.__init__(self)
        self.smtp_host = self.get_param('config.smtp_host', 'localhost')
        self.smtp_port = self.get_param('config.smtp_port', '25')
        self.mail_from = self.get_param('config.from', None, 'Missing sender email address')
        self.use_tls = self.get_param('config.use_tls', False)
        self.mail_password = self.get_param('config.password', None)
        self.mail_to = self.get_param('config.to', None, 'Missing receiver email address')
        self.subject_prefix = self.get_param('config.subject_prefix', None)


    def run(self):
        Responder.run(self)

        title = self.get_param('data.title', None, 'title is missing')
        title = title.encode('utf-8')

        description = self.get_param('data.description', None, 'description is missing')
        description = description.encode('utf-8')
        data = self.get_param('data', None, 'Data is missing')
        data_json = json.dumps(data)

        if self.data_type == 'thehive:case' or self.data_type == 'thehive:alert':
            case_url = 'http://172.16.4.200:30021/index.html#/case/' + data['id'] + '/details'
            data_json += '\n' + case_url
        else:
            self.error('Invalid dataType')

        msg = MIMEMultipart()
        msg['Subject'] = data['id'] + ' ' + title
        msg['From'] = self.mail_from
        msg['To'] = self.mail_to
        msg.attach(MIMEText(data_json, 'plain'))

        if(self.subject_prefix):
            msg['Subject'] = self.subject_prefix + ' ' + msg['Subject']

        if (self.use_tls):
            server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
        else:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.ehlo()

        if (self.mail_password):
            server.login(self.mail_from , self.mail_password)

        server.sendmail(self.mail_from, [self.mail_to], msg.as_string())
        server.quit()
        self.report({'message': 'message sent'})

    def operations(self, raw):
        return [self.build_operation('AddTagToCase', tag='mail sent')]


if __name__ == '__main__':
    AuthMailer().run()
