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
        self.use_tls = self.get_param('config.use_tls', None, 'Missing sender email address')
        self.mail_password = self.get_param('config.password', None)

    def run(self):
        Responder.run(self)

        title = self.get_param('data.title', None, 'title is missing')
        title = title.encode('utf-8')

        description = self.get_param('data.description', None, 'description is missing')
        description = description.encode('utf-8')
        data = self.get_param('data', None, 'Data is missing')
        data_json = json.dumps(data)


        mail_to = None
        if self.data_type == 'thehive:case':
            # Search recipient address in tags
            tags = self.get_param('data.tags', None, 'recipient address not found in tags')
            mail_tags = [t[5:] for t in tags if t.startswith('mail:')]
            case_url = 'http://172.16.4.200:30021/index.html#/case/' + data['id'] + '/details'
            data_json += '\n' + case_url
            if mail_tags:
                mail_to = mail_tags.pop()
            else:
                self.error('recipient address not found in observables')
        elif self.data_type == 'thehive:alert':
            # Search recipient address in artifacts
            artifacts = self.get_param('data.artifacts', None, 'recipient address not found in observables')
            mail_artifacts = [a['data'] for a in artifacts if a.get('dataType') == 'mail' and 'data' in a]
            if mail_artifacts:
                mail_to = mail_artifacts.pop()
            else:
                self.error('recipient address not found in observables')
        else:
            self.error('Invalid dataType')

        msg = MIMEMultipart()
        msg['Subject'] = title
        msg['From'] = self.mail_from
        msg['To'] = mail_to
        msg.attach(MIMEText(data_json, 'plain'))


        if (self.use_tls):
            server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
        else:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.ehlo()

        if (self.mail_password):
            server.login(self.mail_from , self.mail_password)

        server.sendmail(self.mail_from, [mail_to], msg.as_string())
        server.quit()
        self.report({'message': 'message sent'})

    def operations(self, raw):
        return [self.build_operation('AddTagToCase', tag='mail sent')]


if __name__ == '__main__':
    AuthMailer().run()
