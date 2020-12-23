import smtplib
#from secrets import username, password, emails
from .secrets import get_secrets

username, password, mail_list = get_secrets()

def send_email(recent_price, percent_reduction, email_list=mail_list):
    
    gmail_user = username
    gmail_password = password

    #email properties
    sent_from = gmail_user
    to = email_list
    subject = 'Alert for reduced in price'
    email_text = "The price fell from yesterdays close " + \
        f"{recent_price} by {round(percent_reduction*100, 2)} percent."

    #email send request
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()

        print ('Email sent!')
    except Exception as e:
        print(e)
        print ('Something went wrong...')