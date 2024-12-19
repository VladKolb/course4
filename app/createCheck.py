from reportlab.lib.pagesizes import A4, letter, landscape, A5
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class CreateCheck:
   def __init__(self, name = "", surname = "", total="", order = "", fio ="", date="", time = "", nop="", rname="", delivery="" ):
      self.name = name
      self.surname = surname
      self.total = total
      self.order = order
      self.fio = fio
      self.date = date
      self.time = time
      self.nop = nop
      self.rname = rname
      self.delivery = delivery


   def createCheckForPack(self):
      pdfmetrics.registerFont(TTFont('Roboto', 'app/fonts/Roboto-Black.ttf'))

      file_path = "app/checks/check.pdf"
      page_size = landscape(A5)

      
      width, height = page_size

      c = canvas.Canvas(file_path, pagesize=page_size)

      # Установка цвета текста
      c.setFillColorRGB(0, 0, 0)  # черный цвет

      # Установка шрифта и размера
      c.setFont("Roboto", 12)

      # Определение стартовой позиции для текста
      x, y = 50, height - 50

      # Создание списка строк с информацией
      content = [
            f"Имя: {self.name}",
            f"Фамилия: {self.surname}",
            f"Заказ: {self.order}",
            f"Сумма: {self.total}",
            f"{self.delivery}"
        ]

      # Построчное добавление информации на страницу
      for line in content:
         c.drawString(x, y, line)
         y -= 15  # уменьшение координаты y для следующей строки


      # Благодарственный текст
      thank_you_text = "Благодарим за заказ в нашем сервисе!"
      c.drawString(50, 50, thank_you_text)

      # Сохранение PDF
      c.save()

      return True
   
   def createCheckForTable(self):
      pdfmetrics.registerFont(TTFont('Roboto', 'app/fonts/Roboto-Black.ttf'))

      file_path = "app/checks/check.pdf"
      page_size = landscape(A5)

      
      width, height = page_size

      c = canvas.Canvas(file_path, pagesize=page_size)

      # Установка цвета текста
      c.setFillColorRGB(0, 0, 0)  # черный цвет

      # Установка шрифта и размера
      c.setFont("Roboto", 12)

      # Определение стартовой позиции для текста
      x, y = 50, height - 50

      # Создание списка строк с информацией
      content = [
            f"В : {self.rname}",
            f"ФИО: {self.fio}",
            f"Дата: {self.date}",
            f"Время: {self.time}",
            f"На количество человек: {self.nop}"
        ]

      # Построчное добавление информации на страницу
      for line in content:
         c.drawString(x, y, line)
         y -= 15  # уменьшение координаты y для следующей строки


      # Благодарственный текст
      thank_you_text = "Благодарим за бронирование столика!"
      c.drawString(50, 50, thank_you_text)

      # Сохранение PDF
      c.save()

      return True

if __name__ == '__main__':
   sc = CreateCheck()
   sc.createCheck()