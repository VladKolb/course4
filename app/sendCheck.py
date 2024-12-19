import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email import encoders


class SendCheck:
   def __init__(self, receiver_email, sender_email = "vladuceba@gmail.com", sender_password = 'ltes vnnd mwkn lttk'):
      self.receiver_email = receiver_email
      self.sender_email = sender_email
      self.sender_password = sender_password
   
   def sendCheck(self):
      print(self.receiver_email)
      
      subject = 'Чек'
      body = ''

      message = MIMEMultipart()
      message['From'] = self.sender_email
      message['To'] = self.receiver_email
      message['Subject'] = subject

      message.attach(MIMEText(body, 'plain'))

      try:
         attachment_path = 'app/checks/check.pdf'
         with open(attachment_path, 'rb') as attachment:
            part = MIMEApplication(attachment.read(), Name='Чек.pdf')
            part['Content-Disposition'] = f'attachment; filename=Чек.pdf'
            message.attach(part)
      except Exception as e:
         print(f'Ошибка при добавлении файла: {e}')
      finally:
         if attachment:
            attachment.close()

      try:
         server = smtplib.SMTP('smtp.gmail.com', 587)
         server.starttls()
         server.login(self.sender_email, self.sender_password)
         server.sendmail(self.sender_email, self.receiver_email, message.as_string())
         print('Письмо успешно отправлено')
      except Exception as e:
         print(f'Ошибка при отправке письма: {e}')
      finally:
         server.quit()
      
      return True


if __name__ == "__main__":
   ver = SendCheck("brawlerfrank388@gmail.com")
   ver.sendCheck()
   # print(ver.verify())
