import smtplib

gmail_user = 'info@ygotrader.com'
gmail_password = 'Philvern7$'

sent_from = gmail_user
to = ['maciekjanowski@me.com']
subject = 'Script Crash'
body = 'One of the scripts crashed.'

email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, body)

try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    server.sendmail(sent_from, to, email_text)
    server.close()

    print('Email sent!')
except Exception as e:
    print('Something went wrong...', e)