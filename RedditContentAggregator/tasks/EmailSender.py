import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Utils import EmailConfigs

class EmailSender:

    def __init__(self, emailRecipients, emailBody, emailSubject):
        self.emailRecipients = emailRecipients
        self.emailBody = emailBody
        self.emailSubject = emailSubject

    def sendEmail(self):
        # Create a text/plain message from the given email body
        msg = MIMEMultipart("alternative")
        email_body = MIMEText(self.emailBody, "html")  # turn the defined email body into html MIMEText object
        msg.attach(email_body)

        # me == the sender's email address
        # you == the recipient's email address
        msg['Subject'] = self.emailSubject
        msg['From'] = 'suqhprojects@gmail.com'
        msg['To'] = ','.join(self.emailRecipients) # can be a list of one or more recipients (concat into a str)

        # Send the message via our own SMTP server.
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()  # start TLS for security reason
        s.login(user=EmailConfigs.username, password=EmailConfigs.password)

        s.send_message(msg)
        s.quit()