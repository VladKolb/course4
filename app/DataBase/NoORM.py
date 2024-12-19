import psycopg2
from typing_extensions import List, OrderedDict
from datetime import datetime, date, time, timedelta
import os
import pandas as pd
import json


EXPECTED_COLUMNS = ['pack_name', 'pack_type', 'pack_fillin', 'pack_price', 
            'number_of_people', 'pack_description', 'event_id' ]

class DB:
   def __init__(self, db_name="postgres", user="postgres", password="root"):
      self.connection = psycopg2.connect(dbname=db_name, user=user, password=password)
      self.cursor = self.connection.cursor()

   def __del__(self):
      self.cursor.close()
      self.connection.commit()
      self.connection.close()

   '''INSERT INTO table(name, password, email)  
      VALUES ('name', 'password', 'email')'''
   
   def InsertUser(self, **kwargs):
      keys = [str(i) for i in kwargs.keys()]
      values = [f"'{i}'" for i in kwargs.values()]
      self.cursor.execute(f"INSERT INTO users({','.join(keys)}) VALUES({','.join(values)})")
      self.connection.commit()
   
   def getUser(self, user_id, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      self.cursor.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
      values = [str(elem)  for elem in self.cursor.fetchone()]
      res = {keys[i]:values[i] for i in range(len(keys))}
      if not res:
         print("Пользователь не найден")
         return False
      return res
   
   def getUserByEmail(self, user_email, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      self.cursor.execute(f"SELECT * FROM users WHERE email = '{user_email}' LIMIT 1")
      values = [str(elem)  for elem in self.cursor.fetchone()]
      res = {keys[i]:values[i] for i in range(len(keys))}
      if not res:
         print("Пользователь не найден")
         return False
      return res
   
   def updateUserAvatar(self, avatar, user_id):
      if not avatar:
         return False
      
      try:
         #binary = psycopg2.Binary(avatar)
         self.cursor.execute(f"UPDATE users set picture = '{avatar}' WHERE id = {user_id}")
         self.connection.commit()
      except psycopg2.Error as e:
         print("ERROR " + str(e))
         return False
      return True
   
   def updateUser(self, user_id, **kwargs):
      keys = [str(i)  for i in kwargs.keys()]
      values = [f"'{i}'" for i in kwargs.values()]
      result = [f"{keys[i]} = {values[i]}" for i in range(len(keys))]
      self.cursor.execute(f"UPDATE users SET {', '.join(result)} WHERE id = {user_id}")
      self.connection.commit()
   
   def selectMenu(self, sort, event_id, number, **kwargs) -> List[OrderedDict]:
      keys = [str(elem) for elem in kwargs.keys()]
      if sort == 0:
         self.cursor.execute(f"SELECT {','.join(keys)} from menu WHERE event_id = {event_id} and number_of_people = '{number}' ORDER BY dish_type")
      elif sort == 1:
         self.cursor.execute(f"SELECT {','.join(keys)} from menu WHERE event_id = {event_id} and number_of_people = '{number}' ORDER BY dish_price ASC")
      elif sort == 2:
         self.cursor.execute(f"SELECT {','.join(keys)} from menu WHERE event_id = {event_id} and number_of_people = '{number}' ORDER BY dish_price DESC")
      elif sort == 3:
         self.cursor.execute(f"SELECT {','.join(keys)} from menu WHERE event_id = {event_id} and number_of_people = '{number}' ORDER BY cooking_time ASC")
      elif sort == 4:
         self.cursor.execute(f"SELECT {','.join(keys)} from menu WHERE event_id = {event_id} and number_of_people = '{number}' ORDER BY cooking_time DESC")
      res = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res
   
   def selectPlace(self, sort, event_id, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      if sort == 0:
         self.cursor.execute(f"SELECT {','.join(keys)} from restoraunt WHERE event_id = {event_id}")
      elif sort == 1:
         self.cursor.execute(f"SELECT {','.join(keys)} from restoraunt WHERE event_id = {event_id} ORDER BY rating ASC")
      elif sort == 2:
         self.cursor.execute(f"SELECT {','.join(keys)} from restoraunt WHERE event_id = {event_id} ORDER BY rating DESC")
      res = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res
   
   def setOrder(self, **kwargs):
      keys = [str(i) for i in kwargs.keys()]
      values = [f"'{i}'" for i in kwargs.values()]
      self.cursor.execute(f"INSERT INTO person_order ({','.join(keys)}) VALUES({', '.join(values)})")
      self.connection.commit()

   def getOrders(self, person_id,**kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      self.cursor.execute(f"SELECT {','.join(keys)} from person_order WHERE person_id = {person_id}")
      res = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res

   def aboutOrders(self, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      self.cursor.execute(""" SELECT users.id, users.name, users.phone, users.adress, users.email, users.status, person_order.last_order,
                              COALESCE(SUM(person_order.order_count), 0) AS order_count
                              FROM users
                              LEFT JOIN (SELECT person_id, MAX(last_order) AS last_order, COUNT(*) AS order_count
                              FROM person_order
                              GROUP BY person_id) person_order
                              ON users.id = person_order.person_id
                              GROUP BY users.id, users.name, users.phone, users.adress, users.email, users.status, person_order.last_order
                              ORDER BY users.status;""")
      res = []
      keys.append('last_order')
      keys.append('order_counter')
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res
   
   def setAdmin(self, user_id):
      self.cursor.execute(f"UPDATE users SET status = 'admin' WHERE id = {user_id}")
      self.connection.commit()
      return True
   
   def setUser(self, user_id):
      self.cursor.execute(f"UPDATE users SET status = 'user' WHERE id = {user_id}")
      self.connection.commit()
      return True
   
   def selectEvents(self):
      self.cursor.execute("SELECT event_id, type_of_event from events ORDER BY event_id")
      return self.cursor.fetchall()
   
   def selectNumber(self):
      self.cursor.execute("SELECT DISTINCT number_of_people FROM menu ORDER BY number_of_people")
      return self.cursor.fetchall()
   
   def setEvent(self, **kwargs):
      keys = [str(i) for i in kwargs.keys()]
      values = [f"'{i}'" for i in kwargs.values()]
      self.cursor.execute(f"INSERT INTO events ({','.join(keys)}) VALUES({', '.join(values)})")
      self.connection.commit()
   
   def getEvents(self, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      self.cursor.execute(f"SELECT {','.join(keys)} from events ORDER BY type_of_event")
      res = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res
   
   def deleteEvent(self, event_id):
      self.cursor.execute(f"DELETE FROM events WHERE event_id = {event_id}")
      self.connection.commit()
      self.cursor.execute(f"DELETE FROM menu WHERE event_id = {event_id}")
      self.connection.commit()
      return True
   
   def setMenu(self, **kwargs):
      keys = [str(i) for i in kwargs.keys()]
      values = [f"'{i}'" for i in kwargs.values()]
      self.cursor.execute(f"INSERT INTO menu ({','.join(keys)}) VALUES({', '.join(values)})")
      self.connection.commit()

   def deleteDish(self, dish_id):
      self.cursor.execute(f"DELETE FROM menu WHERE dish_id = {dish_id}")
      self.connection.commit()
      return True
   
   def getMenu(self, id, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      self.cursor.execute(f"SELECT {','.join(keys)} from menu WHERE dish_id = {id}")
      res = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res
   
   def updateMenu(self, dish_id, **kwargs):
      keys = [str(i)  for i in kwargs.keys()]
      values = [f"'{i}'" for i in kwargs.values()]
      result = [f"{keys[i]} = {values[i]}" for i in range(len(keys))]
      self.cursor.execute(f"UPDATE menu SET {', '.join(result)} WHERE dish_id = {dish_id}")
      self.connection.commit()
   
   def rMenu(self, sort, r_id, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      if sort == 0:
         self.cursor.execute(f"SELECT {','.join(keys)} from restoraunt_menu WHERE r_id = {r_id} ORDER BY dish_type")
      elif sort == 1:
         self.cursor.execute(f"SELECT {','.join(keys)} from restoraunt_menu WHERE r_id = {r_id} ORDER BY dish_price ASC")
      elif sort == 2:
         self.cursor.execute(f"SELECT {','.join(keys)} from restoraunt_menu WHERE r_id = {r_id} ORDER BY dish_price DESC")
      elif sort == 3:
         self.cursor.execute(f"SELECT {','.join(keys)} from restoraunt_menu WHERE r_id = {r_id} ORDER BY cooking_time ASC")
      elif sort == 4:
         self.cursor.execute(f"SELECT {','.join(keys)} from restoraunt_menu WHERE r_id = {r_id} ORDER BY cooking_time DESC")
      res = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res
   
   def rEvents(self, r_id, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      self.cursor.execute(f"SELECT {','.join(keys)} from r_events WHERE r_id = {r_id}")
      res = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res
   
   def updateViews(self, r_id, views):
      self.cursor.execute(f"UPDATE restoraunt SET r_views = {views} WHERE restoraunt_id = {r_id}")
      self.connection.commit()
   
   def setRest(self, **kwargs):
      keys = [str(i) for i in kwargs.keys()]
      values = [f"'{i}'" for i in kwargs.values()]
      self.cursor.execute(f"INSERT INTO restoraunt ({','.join(keys)}) VALUES({', '.join(values)})")
      self.connection.commit()

   def deleteRest(self, r_id):
      self.cursor.execute(f"DELETE FROM restoraunt WHERE restoraunt_id = {r_id}")
      self.connection.commit()
      self.cursor.execute(f"DELETE FROM restoraunt_menu WHERE r_id = {r_id}")
      self.connection.commit()
      return True

   def getRest(self, r_id, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      self.cursor.execute(f"SELECT {','.join(keys)} from restoraunt WHERE restoraunt_id = {r_id}")
      res = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res
   
   def updateRest(self, r_id, **kwargs):
      keys = [str(i)  for i in kwargs.keys()]
      values = [f"'{i}'" for i in kwargs.values()]
      result = [f"{keys[i]} = {values[i]}" for i in range(len(keys))]
      self.cursor.execute(f"UPDATE restoraunt SET {', '.join(result)} WHERE restoraunt_id = {r_id}")
      self.connection.commit()

   def deleteQuery(self, table, idname, id):
      self.cursor.execute(f"DELETE FROM {table} WHERE {idname} = {id}")
      self.connection.commit()
      return True
   
   def setQuery(self, table, **kwargs):
      keys = [str(i) for i in kwargs.keys()]
      values = [f"'{i}'" for i in kwargs.values()]
      self.cursor.execute(f"INSERT INTO {table} ({','.join(keys)}) VALUES({', '.join(values)})")
      self.connection.commit()
   
   def getQuery(self, table, idname, id, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      self.cursor.execute(f"SELECT {','.join(keys)} from {table} WHERE {idname} = {id}")
      res = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res
   
   def updateQuery(self, table, idname, id, **kwargs):
      keys = [str(i)  for i in kwargs.keys()]
      values = [f"'{i}'" for i in kwargs.values()]
      result = [f"{keys[i]} = {values[i]}" for i in range(len(keys))]
      self.cursor.execute(f"UPDATE {table} SET {', '.join(result)} WHERE {idname} = {id}")
      self.connection.commit()
      return True

   def searchingRest(self, string, event_id, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      result = []
      self.cursor.execute(f"SELECT restoraunt_name from restoraunt WHERE event_id = {event_id}")
      for elem in self.cursor.fetchall():
         if string in elem[0]:
            result.append(f"'{str(elem[0])}'") 
      if result == []:
         return False
      self.cursor.execute(f"SELECT {','.join(keys)} from restoraunt WHERE restoraunt_name IN ({','.join(result)}) and event_id = {event_id} ORDER BY restoraunt_id")
      res = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res

   def searchingRMenu(self, string, r_id, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      result = []
      self.cursor.execute(f"SELECT dish_name from restoraunt_menu WHERE r_id = {r_id}")
      for elem in self.cursor.fetchall():
         if string in elem[0]:
            result.append(f"'{str(elem[0])}'") 
      if result == []:
         return False
      self.cursor.execute(f"SELECT {','.join(keys)} from restoraunt_menu WHERE dish_name IN ({','.join(result)}) and r_id = {r_id} ORDER BY r_menu_id")
      res = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res
   
   def getFilters(self, category, table, idname, id):
      self.cursor.execute(f"SELECT {category} from {table} where {idname} = {id}")
      res = list()
      res1 = set()
      for elem in self.cursor.fetchall():
         res += elem
         res1.add(res.pop()) 
      return res1
   
   def manyFilterRest(self, filter, sort, event_id, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      if sort == 0:
         self.cursor.execute(f"SELECT {','.join(keys)} from restoraunt WHERE event_id = {event_id} AND restoraunt_type = {' OR restoraunt_type = '.join(filter)} ORDER BY restoraunt_type")
      elif sort == 1:
         self.cursor.execute(f"SELECT {','.join(keys)} from menu WHERE event_id = {event_id} AND restoraunt_type = {' OR restoraunt_type = '.join(filter)} ORDER BY rating ASC")
      elif sort == 2:
         self.cursor.execute(f"SELECT {','.join(keys)} from menu WHERE event_id = {event_id} AND restoraunt_type = {' OR restoraunt_type = '.join(filter)} ORDER BY rating DESC")
      res = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res

   def oneFilterRest(self, filter, sort, event_id, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      if sort == 0:
         self.cursor.execute(f"SELECT {','.join(keys)} from restoraunt WHERE restoraunt_type = '{filter}' AND event_id = {event_id} ORDER BY restoraunt_type")
      elif sort == 1:
         self.cursor.execute(f"SELECT {','.join(keys)} from menu WHERE restoraunt_type = '{filter}' AND event_id = {event_id} ORDER BY rating ASC")
      elif sort == 2:
         self.cursor.execute(f"SELECT {','.join(keys)} from menu WHERE restoraunt_type = '{filter}' AND event_id = {event_id} ORDER BY rating DESC")
      res = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res
   
   def updatePassword(self, email, password):
      self.cursor.execute(f"UPDATE users SET password = '{password}' WHERE email = '{email}' ")
      self.connection.commit()
      return True
   
   def selectViews(self, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      self.cursor.execute(f"SELECT {','.join(keys)} from restoraunt")
      res = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res

   def addView(self, event_id):
      self.cursor.execute(f"SELECT view_count FROM events WHERE event_id = {event_id}")
      current_count = self.cursor.fetchone()[0]
      new_count = current_count + 1
      self.cursor.execute(f"UPDATE events SET view_count = {new_count} WHERE event_id = {event_id}")
      self.connection.commit()

      return new_count 
   
   def selectViewsEvent(self, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      self.cursor.execute(f"SELECT {','.join(keys)} from events")
      res = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res
   
   def json(self):
      timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
      json_filename = f"flask_course_{timestamp}.json"   
      self.cursor.execute( """SELECT table_name
                              FROM information_schema.tables
                              WHERE table_schema = 'public'""")
      table_names = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         table_names.append(values[0])
      
      with open(os.path.join("app/jsonfiles/", json_filename), "w", encoding='utf-8') as f:
         for name in table_names:
            self.cursor.execute( f"""SELECT json_agg(t) FROM (
                                 SELECT * FROM {name}
                                 ) t;""")
            res = self.cursor.fetchall()
            if res:
               for elem in res:
                  if elem[0] == None:
                     continue
                  elem = elem[0][0] 
                  f.write(str(elem).replace("'", '"'))
      return json_filename
   
   def selectPack(self, event_id, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      self.cursor.execute(f"SELECT {', '.join(keys)} FROM packs WHERE event_id = {event_id}")
      res = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res
   
   def setPack(self, **kwargs):
      keys = [str(i) for i in kwargs.keys()]
      values = [f"'{i}'" for i in kwargs.values()]
      self.cursor.execute(f"INSERT INTO packs ({','.join(keys)}) VALUES({', '.join(values)})")
      self.connection.commit()
      return True

   def deletePack(self, pack_id):
      self.cursor.execute(f"DELETE FROM packs WHERE pack_id = {pack_id}")
      self.connection.commit()
      self.cursor.execute(f"DELETE FROM pack_product_link WHERE pack_id = {pack_id}")

   def selectProduct(self, event_id, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      self.cursor.execute(f"SELECT {', '.join(keys)} FROM p_fillin WHERE event_id = {event_id}")
      res = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res
   
   def addFillin(self, id, **kwargs):
      keys = [str(i) for i in kwargs.keys()]
      values = [f"{i}" for i in kwargs.values()]
      self.cursor.execute(f"SELECT product_id FROM pack_product_link WHERE pack_id = {id}")
      res = self.cursor.fetchall()
      self.cursor.execute(f"SELECT quantity FROM pack_product_link WHERE pack_id = {id} and product_id = {int(values[1])}")
      res1 = self.cursor.fetchone()
      if res1 != None: 
         quantities = list(res1)
         quantities = int(quantities[0])
         for elem in res:
            if int(values[1]) in elem and int(values[0]) == id:
               new_quantity = quantities + int(values[2])
               self.cursor.execute(f"UPDATE pack_product_link SET quantity = {new_quantity} WHERE pack_id = {id} and product_id = {int(values[1])}")
               self.connection.commit()
               return True
      self.cursor.execute(f"INSERT INTO pack_product_link ({','.join(keys)}) VALUES ({', '.join(values)})")
      self.connection.commit()
      return True
   
   def selectProdToAdd(self, pack_id, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      self.cursor.execute(f"""SELECT p.{(', p.').join(keys)}, ppl.quantity from 
                              p_fillin p
                              INNER JOIN pack_product_link ppl ON p.product_id = ppl.product_id
                              WHERE ppl.pack_id = {pack_id};""")
      res = []
      keys.append('quantity')
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res
   
   def updatePack(self, pack_id, **kwargs):
      keys = [str(i)  for i in kwargs.keys()]
      values = [f"'{i}'" for i in kwargs.values()]
      result = [f"{keys[i]} = {values[i]}" for i in range(len(keys))]
      self.cursor.execute(f"UPDATE packs SET {', '.join(result)} WHERE pack_id = {pack_id}")
      self.connection.commit()
      return True
   
   def updateQ(self, quantity, pack_id, product_id):
      self.cursor.execute(f"UPDATE pack_product_link SET quantity = {quantity} WHERE pack_id = {pack_id} and product_id = {product_id}")
      self.connection.commit()
      return True
   
   def deleteFillin(self, product_id, pack_id):
      self.cursor.execute(f"DELETE FROM pack_product_link WHERE pack_id = {pack_id} and product_id = {product_id}")
      self.connection.commit()
      return True

   def setProd(self, **kwargs):
      keys = [str(i) for i in kwargs.keys()]
      values = [f"'{i}'" for i in kwargs.values()]
      self.cursor.execute(f"INSERT INTO p_fillin ({','.join(keys)}) VALUES({', '.join(values)})")
      self.connection.commit()
      return True

   def deleteProd(self, product_id):
      self.cursor.execute(f"DELETE FROM p_fillin WHERE product_id = {product_id}")
      self.connection.commit()
      return True
   
   def updateProd(self, product_id, **kwargs):
      keys = [str(i)  for i in kwargs.keys()]
      values = [f"'{i}'" for i in kwargs.values()]
      result = [f"{keys[i]} = {values[i]}" for i in range(len(keys))]
      self.cursor.execute(f"UPDATE p_fillin SET {', '.join(result)} WHERE product_id = {product_id}")
      self.connection.commit()
      return True
   
   def setTOrder(self, **kwargs):
      keys = [str(i) for i in kwargs.keys()]
      values = [f"'{i}'" for i in kwargs.values()]
      self.cursor.execute(f"INSERT INTO table_order ({','.join(keys)}) VALUES({', '.join(values)})")
      self.connection.commit()
      return True
   
   def getTOrders(self, user_id, **kwargs):
      keys = [str(elem) for elem in kwargs.keys()]
      self.cursor.execute(f"SELECT {','.join(keys)} from table_order WHERE t_order_user_id = {user_id}")
      res = []
      for elem in self.cursor.fetchall():
         values = [str(elem)  for elem in elem]
         res.append({keys[i]:values[i] for i in range(len(keys))})
      return res
   
   def minusTable(self, restoraunt_id):
      self.cursor.execute(f"SELECT free_tables FROM restoraunt WHERE restoraunt_id = {restoraunt_id}")
      current_count = self.cursor.fetchone()[0]
      new_count = current_count - 1
      self.cursor.execute(f"UPDATE restoraunt SET free_tables = {new_count} WHERE restoraunt_id = {restoraunt_id}")
      self.connection.commit()
   
   def plusplus(self, r_id):
      self.cursor.execute(f"SELECT free_tables FROM restoraunt WHERE restoraunt_id = {r_id}")
      current_count = self.cursor.fetchone()[0]
      new_count = current_count + 1
      self.cursor.execute(f"UPDATE restoraunt SET free_tables = {new_count} WHERE restoraunt_id = {r_id}")
      self.connection.commit()

   def delOrder(self, order_id):
      self.cursor.execute(f"DELETE FROM table_order WHERE t_order_id = {order_id}")
      self.connection.commit()
      return True
   

   def plusTable(self, r_id):
      self.cursor.execute("SELECT t_order_id, t_order_date, t_order_time FROM table_order")
      current_datetime = datetime.now()
      for elem in self.cursor.fetchall():
         print(list(elem))
         res = list(elem)
         target_date = res[1]
         target_time = res[2]
         target_datetime = datetime.combine(target_date, target_time)
         time_difference = target_datetime - current_datetime
         if time_difference.total_seconds() < 0:
            DB.plusplus(self, r_id)
   
      return True

   def getUserForExel(self, **kwargs):
      #self.cursor.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
      df = pd.read_sql_query(""" SELECT users.id, users.name, users.phone, users.adress, users.email, users.status, person_order.last_order,
                              COALESCE(SUM(person_order.order_count), 0) AS order_count
                              FROM users
                              LEFT JOIN (SELECT person_id, MAX(last_order) AS last_order, COUNT(*) AS order_count
                              FROM person_order
                              GROUP BY person_id) person_order
                              ON users.id = person_order.person_id
                              GROUP BY users.id, users.name, users.phone, users.adress, users.email, users.status, person_order.last_order
                              ORDER BY users.status;""", self.connection)
      return df
   
   def import_json_to_postgres(self, file_path, table_name):
      with open(file_path, 'r', encoding='utf-8') as json_file:
         data = json.load(json_file)
         

      if set(data.keys()) != set(EXPECTED_COLUMNS) and len(data) != 7:
         raise ValueError('Неверные столбцы в JSON-файле. Ожидались: Имя, Фамилия, Отчество, Год рождения.')

      data['pack_price'] = str(data['pack_price'])
      data['number_of_people'] = str(data['number_of_people'])
      data['event_id'] = str(data['event_id'])

      columns = ', '.join(data.keys())
      values = [f"'{i}'" for i in data.values()]
      print(columns, values, sep='\n')
      
      
      self.cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({', '.join(values)})")



if __name__ == "__main__":
   db = DB()
   print(db.plusTable(1))   