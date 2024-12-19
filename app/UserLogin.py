from flask_login import UserMixin
from flask import url_for

class Userlogin(UserMixin):
   def fromDB(self, user_id, db):
      self.__user = db.getUser(user_id, id="", name="", password = "", email="", phone="", picture="", adress="", events="", status="")
      return self
   
   def create(self, user):
      self.__user = user
      return self
   
   def get_id(self):
      return str(self.__user['id'])
   
   def get_name(self):
      return str(self.__user['name'])
   
   def get_email(self):
      return str(self.__user['email'])
   
   def get_phone(self):
      return str(self.__user['phone'])
   
   def get_adress(self):
      return str(self.__user['adress'])
   
   def get_events(self):
      return str(self.__user['events'])
   
   def get_status(self):
      return str(self.__user['status'])
   
   def getAvatar(self, app):
      img = None
      if self.__user['picture'] == 'None':
         try:
            with app.open_resource(app.root_path + url_for('static', filename='alian.png'), "rb") as f:
               img = f.read()
         except FileNotFoundError as e:
            print("Не найден аватар по умолчанию: " + str(e))
      else:
         try:
            with app.open_resource(app.root_path + url_for('static', filename=f'avas/{self.__user["picture"]}'), "rb") as f:
               img = f.read()
         except FileNotFoundError as e:
            print("Не найден аватар по умолчанию: " + str(e))
      return img            
   
   def verifyExt(self, filename):
      ext = filename.rsplit('.', 1)[1]
      if ext == "png" or ext == "PNG":
         return True
      return False