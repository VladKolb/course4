import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

class Verify:
   def __init__(self, receiver_email, sender_email = "vladuceba@gmail.com", sender_password = 'ltes vnnd mwkn lttk'):
      self.receiver_email = receiver_email
      self.sender_email = sender_email
      self.sender_password = sender_password
   
   def verify(self):
      print(self.receiver_email)
      verify_number = random.randint(100000, 999999)
      
      subject = 'Верификация'
      body = f'Ваш код верификации - {verify_number}'

      message = MIMEMultipart()
      message['From'] = self.sender_email
      message['To'] = self.receiver_email
      message['Subject'] = subject

      message.attach(MIMEText(body, 'plain'))

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
      
      return verify_number


if __name__ == "__main__":
   ver = Verify("brawlerfrank388@gmail.com")
   ver.verify()
   # print(ver.verify())
