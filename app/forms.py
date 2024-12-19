import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, FloatField, validators, RadioField, TimeField, DateField
from wtforms.validators import Length, DataRequired, Email, NumberRange
from datetime import datetime, timedelta, date
from wtforms_components import DateRange

def validate_clear_name(form, field):
    name = field.data
    if not name.replace(" ", "").isalpha():
        raise validators.ValidationError("Имя должно состоять только из букв и пробелов")

def validate_clear_email(form, field):
    email = field.data
    # Дополнительная проверка на разборчивость email
    # Например, можно проверить, что в имени пользователя и домене нет специальных символов и проч.
    if not email.replace("@", "").replace(".", "").isalnum():
        raise validators.ValidationError("Некорректный формат email")
    
def validate_phone(form, field):
      phone = field.data
      # Проверка формата номера и наличия только цифр
      if not (phone.startswith("+375-") and phone[4] == '-' and phone[7] == '-' and phone[11] == '-' and phone[14] == '-' and phone[1:4].isdigit() and phone[5:7].isdigit() and phone[8:11].isdigit() and phone[12:14].isdigit() and phone[15:].isdigit()):
         raise validators.ValidationError("Некорректный формат телефона")

class RegisterForm(FlaskForm):
   name = StringField("Имя: ", validators=[DataRequired(), Length(min = 2, max = 30, message="Имя должно быть от 2 до 30 символов"), validate_clear_name])
   email = StringField("Email: ", validators=[DataRequired(), Email("Некоректный Email!"), validate_clear_email])
   password = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max = 20, message="Пароль должени быть от 4 до 20 символов")])
   phone = StringField("Телефон: ", validators=[DataRequired(), Length(min = 17, max = 18, message="Телефон должен быть 17 символов"),validate_phone])
   submit = SubmitField("Зарегистрироваться")

class LoginForm(FlaskForm):
   email = StringField("Email: ", validators=[DataRequired(), Email(), validate_clear_email])
   password = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=20, message="Пароль должени быть от 4 до 20 символов")])
   sumbit = SubmitField("Войти")

class ChangeForm(FlaskForm):
   name = StringField(validators=[DataRequired(), Length(min= 2, max=30, message="Имя должно быть от 2 до 30 символов"), validate_clear_name])
   email = StringField(validators=[DataRequired(), Email("Некоректный Email!"), validate_clear_email])
   phone = StringField("Телефон: ", validators=[DataRequired(), Length(min= 17, max=18),validate_phone])
   adress = StringField(validators=[DataRequired(),  Length(min= 2, max=30)])
   events = StringField(validators=[DataRequired(), Length(min= 2, max=30 )])
   sumbit = SubmitField("Подтвердить")


class ChooseEvent(FlaskForm):
   
   def __init__(self, event_chooses, number_of_people, *args, **kwargs):
      super(ChooseEvent, self).__init__(*args, **kwargs)
      self.event_chooses = event_chooses
      self.number_of_people_chooses = number_of_people
      self.events.choices = event_chooses
      self.number_of_people.choices = number_of_people

   place_chooses = [
      ('atHome', "Дома"),
      ('outside', 'Вне дома')
   ]


   events = SelectField('Выберете мероприятие: ',choices=[], validators=[DataRequired()])
   number_of_people = SelectField('Выберете количество людей на мероприятии: ', choices=[])
   places = SelectField('Укажите, где вы хотите провести мероприятие: ', choices=place_chooses)
   submit = SubmitField("Подтвердить")

class CartForm(FlaskForm):
   town_choices = [
      ('Минск', 'Минск'),
      ('Могилёв', 'Могилёв'),
      ('Брест', 'Брест')
   ]

   payment_choices = [("Наличные", "Наличные"), ("Карта", "Карта")]


   name = StringField(validators=[DataRequired(), Length(min=2, max=15), validate_clear_name])
   surname = StringField(validators=[DataRequired(), Length(min=2, max=15), validate_clear_name])
   email = StringField(validators=[DataRequired(), Email(),Length(min=2, max=50), validate_clear_email])
   phone = StringField(validators=[DataRequired(), Length(min=17, max=18), validate_phone])
   adress = StringField(validators=[DataRequired(), Length(min= 17, max=18)])
   town = SelectField(validators=[DataRequired()], choices=town_choices)
   payment = RadioField("Способ оплаты:", choices=payment_choices, validators=[validators.DataRequired()])
   submit = SubmitField("Подтвердить")

class CartChangeForm(FlaskForm):
   town_choices = [
      ('minsk', 'Минск'),
      ('mogilev', 'Могилёв'),
      ('brest', 'Брест')
   ]

   payment_choices = [("Наличные", "Наличные"), ("Карта", "Карта")]


   name = StringField(validators=[DataRequired(), Length(min=2, max=15), validate_clear_name])
   surname = StringField(validators=[DataRequired(), Length(min=2, max=15), validate_clear_name])
   email = StringField(validators=[DataRequired(), Email(),Length(min=2, max=50), validate_clear_email])
   phone = StringField(validators=[DataRequired(), Length(min=17, max=18), validate_phone])
   adress = StringField(validators=[DataRequired(), Length(min= 17, max=18)])
   town = SelectField(validators=[DataRequired()], choices=town_choices)
   payment = RadioField("Способ оплаты:", choices=payment_choices, validators=[validators.DataRequired()])
   price = FloatField(validators=[DataRequired()])
   order_text = StringField(validators=[DataRequired()])
   submit = SubmitField("Подтвердить")

class SearchForm(FlaskForm):
   search = StringField(validators=[validate_clear_name])
   submit = SubmitField("Найти")

class Checker(FlaskForm):
   checker = BooleanField()
   submit = SubmitField()

class AddEvent(FlaskForm):
   event_name = StringField(validators=[DataRequired(), Length(min = 3, max = 20), validate_clear_name])
   submit = SubmitField()

class ChangeRestForm(FlaskForm):
   place_name = StringField(validators=[DataRequired(), Length(min = 3, max = 20)])
   place_availability = StringField(validators=[DataRequired(), Length(min = 3, max = 20)])
   place_scheldue = StringField(validators=[DataRequired(), Length(min = 3, max = 20)])
   place_adress = StringField(validators=[DataRequired(), Length(min = 3, max = 20)])
   place_type = StringField(validators=[DataRequired(), Length(min = 3, max = 20)])
   submit = SubmitField()

class AddMenu(FlaskForm):
   dish = StringField(validators=[DataRequired(), Length(min = 3, max = 20)])
   ingredients = StringField(validators=[DataRequired()])
   dish_price = StringField(validators=[DataRequired()])
   cooking_time = IntegerField()
   how_to_cook = StringField(validators=[DataRequired()])
   dish_type = StringField(validators=[DataRequired(), Length(min = 3, max = 20)])
   submit = SubmitField()

class AddPack(FlaskForm):
   pack_name = StringField(validators=[DataRequired(), Length(max=100)])
   pack_description = StringField(validators=[DataRequired()])
   submit = SubmitField()

class AddPackJSON(FlaskForm):
   pack_name = StringField(validators=[DataRequired(), Length(max=100)])
   pack_type = StringField(validators=[DataRequired(), Length(max=50)])
   pack_fillin = StringField(validators=[DataRequired()])
   pack_price = FloatField(validators=[DataRequired()])
   number_of_people = IntegerField(validators=[DataRequired(), NumberRange(min=0, max=5)])
   pack_description = StringField(validators=[DataRequired()])
   submit = SubmitField()

class AddProd(FlaskForm):
   product_name = StringField(validators=[DataRequired(), Length(max=100)])
   product_price = FloatField(validators=[DataRequired()])
   product_type = StringField(validators=[DataRequired(), Length(max=50)])
   submit = SubmitField()

class UpdateProd(FlaskForm):
   product_name = StringField(validators=[DataRequired(), Length(max=100)])
   product_price = FloatField(validators=[DataRequired()])
   product_type = StringField(validators=[DataRequired(), Length(max=50)])
   submit = SubmitField()


class ChangeMenuForm(FlaskForm):
   dish = StringField(validators=[DataRequired(), Length(min = 3, max = 20)])
   ingredients = StringField(validators=[DataRequired()])
   dish_price = StringField(validators=[DataRequired()])
   cooking_time = IntegerField(validators=[DataRequired(), validators.NumberRange(min=0, max=1000)])
   how_to_cook = StringField(validators=[validators.URL(message="Введите корректную ссылку")])
   dish_type = StringField(validators=[DataRequired(), Length(min = 3, max = 20)])
   submit = SubmitField()

class ForgottenPassword(FlaskForm):
   verify = StringField("Код", validators=[DataRequired(), Length(min=6, max=7)])
   new_password = PasswordField("Пароль", validators=[DataRequired(), Length(min=4, max = 20, message="Пароль должени быть от 4 до 20 символов")])
   repeat = PasswordField("Повторите пароль", validators=[DataRequired(), Length(min=4, max = 20, message="Пароль должени быть от 4 до 20 символов")])
   submit = SubmitField()

class SendVerify(FlaskForm):
   email = StringField("Email", validators=[Email()])
   submit = SubmitField()

class CreateRest(FlaskForm):
   r_name = StringField(validators=[DataRequired(), Length(min = 3, max = 20)])
   r_type = StringField(validators=[DataRequired()])
   r_scheldue = StringField(validators=[DataRequired(), validators.Regexp(r'^[0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9]$', message="Введите корректное расписание в формате HH:mm-HH:mm")])
   r_rating = StringField(validators=[validators.Regexp(r'^[0-5]/5$', message="Введите корректный рейтинг в формате X/5, где X от 0 до 5")])
   r_adress = StringField(validators=[DataRequired()])
   r_contact = StringField(validators=[DataRequired(), Length(min = 17, max = 18, message="Телефон должен быть 17 символов"),validate_phone])
   r_site = StringField(validators=[validators.URL(message="Введите корректную ссылку")])
   submit = SubmitField()

class ChangeRest(FlaskForm):
   r_name = StringField(validators=[DataRequired(), Length(min = 3, max = 20)])
   r_type = StringField(validators=[DataRequired()])
   r_scheldue = StringField(validators=[DataRequired(), validators.Regexp(r'^[0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9]$', message="Введите корректное расписание в формате HH:mm-HH:mm")])
   r_rating = StringField(validators=[validators.Regexp(r'^[0-5]/5$', message="Введите корректный рейтинг в формате X/5, где X от 0 до 5")])
   r_adress = StringField(validators=[DataRequired()])
   r_contact = StringField(validators=[DataRequired(), Length(min = 17, max = 18, message="Телефон должен быть 17 символов"),validate_phone])
   r_site = StringField(validators=[validators.URL(message="Введите корректную ссылку")])
   submit = SubmitField()

class CreateRMenu(FlaskForm):
   dish_name = StringField(validators=[DataRequired(), Length(min = 3, max = 20), validate_clear_name])
   dish_price = FloatField(validators=[validators.NumberRange(min=0, message="Цена должна быть неотрицательным числом")])
   cooking_time = IntegerField(validators=[DataRequired(), validators.NumberRange(min=0, max=1000)])
   dish_description = StringField(validators=[DataRequired()])
   dish_type = StringField(validators=[DataRequired(), Length(min = 3, max = 20)])
   submit = SubmitField()

class UpdateRMenu(FlaskForm):
   dish_name = StringField(validators=[DataRequired(), Length(min = 3, max = 20), validate_clear_name])
   dish_price = FloatField(validators=[validators.NumberRange(min=0, message="Цена должна быть неотрицательным числом")])
   cooking_time = IntegerField(validators=[DataRequired(), validators.NumberRange(min=0, max=1000)])
   dish_description = StringField(validators=[DataRequired()])
   dish_type = StringField(validators=[DataRequired(), Length(min = 3, max = 20)])
   submit = SubmitField()

class InsertREvent(FlaskForm):
   r_event_name = StringField(validators=[DataRequired(), Length(min = 3, max = 20)])
   r_event_day = StringField(validators=[DataRequired(), Length(min = 3, max = 20)])
   r_event_time = StringField()
   r_event_description = StringField()
   submit = SubmitField()

class UpdateREvent(FlaskForm):
   r_event_name = StringField(validators=[DataRequired(), Length(min = 3, max = 20)])
   r_event_day = StringField(validators=[DataRequired(), Length(min = 3, max = 20)])
   r_event_time = StringField(validators=[DataRequired(), validators.Regexp(r'^[0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9]$', message="Введите корректное расписание в формате HH:mm-HH:mm")])
   r_event_description = StringField(validators=[DataRequired()])
   submit = SubmitField()

class SearchForm(FlaskForm):
   search = StringField()
   submit = SubmitField("Найти")

class ForgottenPassword(FlaskForm):
   verify = StringField("Код", validators=[DataRequired()])
   new_password = PasswordField("Пароль", validators=[DataRequired(), Length(min=4, max = 20, message="Пароль должени быть от 4 до 20 символов")])
   repeat = PasswordField("Повторите пароль", validators=[DataRequired(), Length(min=4, max = 20, message="Пароль должени быть от 4 до 20 символов")])
   submit = SubmitField()

class SendVerify(FlaskForm):
   email = StringField("Email", validators=[DataRequired(), Email(), validate_clear_email])
   submit = SubmitField()

class TableOrderForm(FlaskForm):
   
   today = datetime.now().date()
   max_date = today + timedelta(days=10)

   t_order_fio = StringField(validators=[DataRequired(), Length(max=100)])
   t_order_nop = IntegerField(validators=[DataRequired(), NumberRange(min=0, max=5)])
   t_order_date = DateField(format='%Y-%m-%d', validators=[DataRequired(), DateRange(min=date.today(), max=date.today() + timedelta(days=10))])
   t_order_time = TimeField(format='%H:%M', validators=[DataRequired()])
   email = StringField(validators=[DataRequired(), Email()])
   submit = SubmitField()


if __name__ == '__main__':
   event_chooses = [
      ('1', 'День рождения'),
      ('2', 'Пикник'),
      ('3', 'Вечеринка'),
      ('4', 'Барбекю'),
      ('5', 'Азиатская вечеринка')
   ]
   ce = ChooseEvent(event_chooses=event_chooses)
   print(ce.events)