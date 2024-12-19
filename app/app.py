from flask import Flask, render_template, url_for, flash, redirect, request, make_response, session, send_file, jsonify
from DataBase.NoORM import DB
from forms import RegisterForm, LoginForm, ChangeForm, AddPack, AddProd, CartChangeForm, CartForm, Checker, CreateRest, ChangeRest, AddEvent, UpdateRMenu, CreateRMenu, UpdateREvent, InsertREvent, SearchForm, TableOrderForm, ForgottenPassword, SendVerify, UpdateProd, AddPackJSON
from werkzeug.security import generate_password_hash, check_password_hash
from UserLogin import Userlogin
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
import time
from datetime import datetime, timedelta
from verify import Verify
from createCheck import CreateCheck
from sendCheck import SendCheck
import json
import os
import tempfile
import pandas as pd
from io import BytesIO
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretsecretsecret'
app.config['SESSION_TYPE'] = 'filesystem'
db = DB()
MAX_CONTENT_LENGHT = 1024 * 1024
UPLOAD_FOLDER = 'app/jsonfiles'
ALLOWED_EXTENSIONS = {'json'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

EXPECTED_COLUMNS = ['pack_name', 'pack_type', 'pack_fillin', 'pack_price', 
            'number_of_people', 'pack_description', 'event_id' ]

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Userlogin().fromDB(user_id, db)


@app.route("/", methods=["POST", "GET"])
def home():
    information = {'events': db.getEvents(event_id="", type_of_event="")}
    return render_template("home.html", information = information)


@app.route('/packs/<int:event_id>', methods=["POST", "GET"])
def packsPage(event_id):
    info = {"packs": db.selectPack(event_id, pack_id="", pack_name="", pack_type="", pack_fillin="", pack_price="", number_of_people="",
                                    pack_description = ""),
            "page": "packs"}
    return render_template("packsPage.html", info = info, event_id = event_id)


@app.route('/addPack/<int:event_id>', methods=["POST", "GET"])
def addPack(event_id):
    form = AddPack()
    if form.validate_on_submit():
        db.setPack(pack_name=form.pack_name.data, pack_description = form.pack_description.data, event_id = event_id)
        return redirect(url_for("packsPage",  event_id=event_id))
    return render_template("addPack.html", form=form)


@app.route('/deletePack/<int:event_id>/<page>/<int:pack_id>', methods=["POST", "GET"])
def deletePack(event_id, page, pack_id):
    if request.method == "POST":
        db.deletePack(pack_id)
        if page == 'packs':
            return redirect(url_for("packsPage",  event_id = event_id))
    return redirect(url_for('home'))


@app.route('/products_for_add/<int:pack_id>/<int:event_id>', methods=["POST", "GET"])
def pfAdd(pack_id, event_id):
    form = SearchForm()
    info = {"prod": db.selectProduct(event_id, product_id="", product_name="", product_price="", product_type="")}
    return render_template("productList.html", info=info, form = form, event_id = event_id, pack_id = pack_id)


@app.route('/addProd/<int:event_id>/<int:pack_id>', methods=["POST", "GET"])
def addProd(event_id, pack_id):
    form = AddProd()
    if form.validate_on_submit():
        res = db.setProd(product_name = form.product_name.data, product_price = form.product_price.data, 
                         event_id = event_id, product_type = form.product_type.data)
        return redirect(url_for('pfAdd', pack_id = pack_id, event_id = event_id))
    return render_template('addProd.html', form = form)


@app.route('/deleteProd/<int:product_id>/<int:event_id>/<int:pack_id>', methods=["POST", "GET"])
def deleteProd(product_id, event_id, pack_id):
    if request.method == "POST":
        db.deleteProd(product_id)
        return redirect(url_for('pfAdd', pack_id = pack_id, event_id = event_id))
    return redirect(url_for('home'))


@app.route('/updateProd/<int:product_id>/<int:event_id>/<int:pack_id>', methods=["POST", "GET"])
def updateProd(product_id, event_id, pack_id):
    form = UpdateProd()
    information = {"info": db.getQuery('p_fillin', 'product_id', product_id,  product_name = "", product_price = "", product_type = "")}
    if form.validate_on_submit():
        res = db.updateProd(product_id, product_name = form.product_name.data, product_price = form.product_price.data, product_type = form.product_type.data)
        if res:
            flash("Данные обновленны")
            return redirect(url_for('pfAdd', pack_id = pack_id, event_id = event_id))
        else:
            flash("ERROR")
    return render_template("updateProd.html", form=form, information = information)


@app.route('/addFillin/<int:pack_id>/<int:event_id>/<int:product_id>', methods=["POST", "GET"])
def addFillin(pack_id, event_id, product_id):
    quantity = 1
    if request.method == "POST":
        if request.form.get("Add") == "Add":
            quantity = int(request.form['quantity'])
            print(pack_id, product_id, quantity)
            res = db.addFillin(pack_id, pack_id = pack_id, product_id = product_id, quantity = quantity)
            if res:
                print("добавлето в таблицу")
            return redirect(url_for('pfAdd', pack_id=pack_id, event_id=event_id))
        if request.form.get('End') == "End":
            res = db.selectProdToAdd(pack_id, product_id="", product_name='', product_price='', product_type='' )
            text = ""
            total_count = 0
            types = []
            for elem in res:
                text += f"{elem['product_name']} {elem['quantity']} шт ,"
                total_count += float(elem['product_price']) * int(elem['quantity'])
                if elem['product_type'] in types:
                    continue
                types.append(elem['product_type'])
            print(text, total_count, types, sep='\n')
            
            return redirect(url_for("packsPage",  event_id = event_id))

    return redirect(url_for('pfAdd', pack_id=pack_id, event_id=event_id))


@app.route('/accept/<int:pack_id>/<int:event_id>', methods=["POST", "GET"])
def accept(pack_id, event_id):
    if request.method == "POST":
        res = db.selectProdToAdd(pack_id, product_id="", product_name='', product_price='', product_type='' )
        text = ""
        total_count = 0
        types = []
        total_type = ''
        counter = 0
        number_of_people = 2
        for elem in res:
            counter += int(elem['quantity'])
            text += f"{elem['product_name']} {elem['quantity']} шт, "
            total_count += float(elem['product_price']) * int(elem['quantity'])
            if elem['product_type'] in types:
                continue
            types.append(elem['product_type'])
        
        if 5 <= counter <= 10 :
            number_of_people = 5
        elif 10 < counter <= 15:
            number_of_people = 8
        elif 15 < counter <= 20:
            number_of_people = 12
        
        
        if len(types) == 1:
            total_type = types[0]
        else:
            total_type = "Разное"
        
        res = db.updatePack(pack_id, pack_type=total_type, pack_fillin=text, pack_price=total_count, number_of_people=number_of_people)
        return redirect(url_for("packsPage",  event_id = event_id))
    
    return redirect(url_for('pfAdd', pack_id=pack_id, event_id=event_id))


@app.route('/fillin/<int:pack_id>/<int:event_id>', methods=["POST", "GET"])
def fillin(pack_id, event_id):
    info = {'prod': db.selectProdToAdd(pack_id, product_id="", product_name='', product_price='', product_type='' )}
    return render_template('fillin.html', info=info, pack_id=pack_id, event_id = event_id)


@app.route('/deleteFromPack/<int:pack_id>/<int:product_id>/<int:quantity>/<int:event_id>', methods=["POST", "GET"])
def deleteFromPack(pack_id, product_id, quantity, event_id):
    if request.method == "POST":
        if quantity - 1 == 0:
            delete = db.deleteFillin(product_id, pack_id)
            if delete:
                res = db.selectProdToAdd(pack_id, product_id="", product_name='', product_price='', product_type='')
                text = ""
                total_count = 0
                types = []
                total_type = ''
                counter = 0
                number_of_people = 2
                for elem in res:
                    counter += int(elem['quantity'])
                    text += f"{elem['product_name']} {elem['quantity']} шт, "
                    total_count += float(elem['product_price']) * int(elem['quantity'])
                    if elem['product_type'] in types:
                        continue
                    types.append(elem['product_type'])
                
                if 5 <= counter <= 10 :
                    number_of_people = 5
                elif 10 < counter <= 15:
                    number_of_people = 8
                elif 15 < counter <= 20:
                    number_of_people = 12
                
                
                if len(types) == 1:
                    total_type = types[0]
                else:
                    total_type = "Разное"
                
                res = db.updatePack(pack_id, pack_type=total_type, pack_fillin=text, pack_price=total_count, number_of_people=number_of_people)
                return redirect(url_for("fillin",  pack_id=pack_id, event_id=event_id))
        
        elif quantity - 1 > 0:
            quantity -= 1
            delete = db.updateQ(quantity, pack_id, product_id)
            if delete:
                res = db.selectProdToAdd(pack_id, product_id="", product_name='', product_price='', product_type='')
                text = ""
                total_count = 0
                types = []
                total_type = ''
                counter = 0
                number_of_people = 2
                for elem in res:
                    counter += int(elem['quantity'])
                    text += f"{elem['product_name']} {elem['quantity']} шт, "
                    total_count += float(elem['product_price']) * int(elem['quantity'])
                    if elem['product_type'] in types:
                        continue
                    types.append(elem['product_type'])
                
                if 5 <= counter <= 10 :
                    number_of_people = 5
                elif 10 < counter <= 15:
                    number_of_people = 8
                elif 15 < counter <= 20:
                    number_of_people = 12
                
                
                if len(types) == 1:
                    total_type = types[0]
                else:
                    total_type = "Разное"
                
                res = db.updatePack(pack_id, pack_type=total_type, pack_fillin=text, pack_price=total_count, number_of_people=number_of_people)
                return redirect(url_for("fillin",  pack_id=pack_id, event_id=event_id))
        
        
    
    return redirect(url_for('fillin', pack_id=pack_id, event_id=event_id))


@app.route('/addEvent', methods=["POST", "GET"])
def addEvent():
    form = AddEvent()
    if form.validate_on_submit():
        db.setEvent(type_of_event = form.event_name.data)
        return redirect(url_for("home"))
    return render_template("addEvent.html", form=form)


@app.route('/deleteEvent/<int:event_id>', methods=["POST", "GET"])
def deleteEvent(event_id):
    if request.method == "POST":
        db.deleteEvent(event_id)
        return redirect(url_for('home'))
    return redirect(url_for('home'))


@app.route('/barPage/<int:event_id>', methods=["POST", "GET"])
def bar(event_id):
    db.addView(event_id)
    selected_filters = list()
    sort = 0
    filters = db.getFilters("restoraunt_type", "restoraunt", 'event_id', event_id)
    form = SearchForm()
    if request.method == "POST":
        if request.form.get("submit") == "submit":
            information = {"place": db.searchingRest(form.search.data, event_id, restoraunt_id="", restoraunt_type="", restoraunt_name = "", scheldue="", rating="", adress="", contact_number="", restoraunt_site="", r_views="", free_tables=""),
                           "filters": filters}
            if information["place"] == False:
                flash('Такого блюда нету!')
                information["place"] = db.selectPlace(sort, event_id, restoraunt_id="", restoraunt_type="", restoraunt_name = "", scheldue="", rating="", adress="", contact_number="", restoraunt_site="", r_views="", free_tables="")
                return render_template("barPage.html", information=information, event_id = event_id, form = form)
            flash('Успешно')
            return render_template("barPage.html", information=information, event_id = event_id, form = form, selected_filters = selected_filters)
        
        elif request.form.get("rating") == "TopRating":
            sort = 2
            information = { "place" : db.selectPlace(sort, event_id, restoraunt_id="", restoraunt_type="", restoraunt_name = "", scheldue="", rating="", adress="", contact_number="", restoraunt_site="", r_views="", free_tables=""),
                           "filters": filters} 
            return render_template("barPage.html", information=information, event_id = event_id, form = form, selected_filters = selected_filters)

        elif request.form.get("rating") == "BottomRating":
            sort = 1
            information = { "place" : db.selectPlace(sort, event_id, restoraunt_id="", restoraunt_type="", restoraunt_name = "", scheldue="", rating="", adress="", contact_number="", restoraunt_site="", r_views="", free_tables=""),
                           "filters": filters} 
            return render_template("barPage.html", information=information, event_id = event_id, form = form, selected_filters = selected_filters)
    
        elif request.form.get("fil") == "filter":
            selected_filters = [filter for filter in request.form if request.form.get(filter) == 'on']
            print(f"Фильтры {', '.join(selected_filters)}")
            if len(selected_filters) == 0:
                information = { "place" : db.selectPlace(sort, event_id, restoraunt_id="", restoraunt_type="", restoraunt_name = "", scheldue="", rating="", adress="", contact_number="", restoraunt_site="", r_views="", free_tables=""),
                           "filters": filters} 
                return render_template("barPage.html", information=information, event_id = event_id, form = form, selected_filters = selected_filters)
            
            elif len(selected_filters) == 1:
                information = { "place" : db.oneFilterRest(selected_filters[0], sort, event_id, restoraunt_id="", restoraunt_type="", restoraunt_name = "", scheldue="", rating="", adress="", contact_number="", restoraunt_site="", r_views="", free_tables=""),
                           "filters": filters} 
                return render_template("barPage.html", information=information, event_id = event_id, form = form, selected_filters = selected_filters)            
            
            elif len(selected_filters) >= 2:
                new_selected_filters = [f"'{elem}'" for elem in selected_filters]
                print(new_selected_filters)
                information = { "place" : db.manyFilterRest(new_selected_filters, sort, event_id, restoraunt_id="", restoraunt_type="", restoraunt_name = "", scheldue="", rating="", adress="", contact_number="", restoraunt_site="", r_views="", free_tables=""),
                           "filters": filters} 
                return render_template("barPage.html", information=information, event_id = event_id, form = form, selected_filters = selected_filters)
    
    information = { "place" : db.selectPlace(sort, event_id, restoraunt_id="", restoraunt_type="", restoraunt_name = "", scheldue="", rating="", adress="", contact_number="", restoraunt_site="", r_views="", free_tables=""),
                           "filters": filters} 
    return render_template("barPage.html", information=information, event_id = event_id, form = form, selected_filters = selected_filters)


@app.route('/tableOrder/<restoraunt_name>/<int:r_id>', methods=["POST", "GET"])
@login_required
def tableOrder(restoraunt_name, r_id):
    form = TableOrderForm()
    if request.method == "POST":
        print('ZAKAZ')
        res = db.setTOrder(t_order_date=form.t_order_date.data, t_order_time=form.t_order_time.data, t_order_fio = form.t_order_fio.data,
                                t_order_nop=form.t_order_nop.data, t_order_rname = restoraunt_name, t_order_email=form.email.data, t_order_user_id = session['user_id'])
        if res:
            db.minusTable(r_id)
            return redirect(url_for('t_order')) 
    print("NEZAKAZ")
    return render_template('tableOrder.html', restoraunt_name = restoraunt_name, form = form)


@app.route('/t_orders', methods=["POST", "GET"])
@login_required
def t_order():
    info = {"order": db.getTOrders(session['user_id'], t_order_id="", t_order_date="", t_order_time="", t_order_fio = "",
                                t_order_nop="", t_order_rname = "", t_order_email="")}
    return render_template('t_orders.html', info = info, )


@app.route('/sendTCheck/<fio>/<date>/<time>/<int:nop>/<rname>/<email>', methods=["POST", "GET"])
def sendTCheck(fio, date, time, nop, rname, email):
    if request.method == "POST":
        create = CreateCheck(fio=fio, date=date, time=time, nop=nop, rname = rname)
        create.createCheckForTable()
        if create:
            print("EXELENT")
        else:
            print("ERROR")
        send = SendCheck(email)
        send.sendCheck()
        if send:
            print("EXELENT")
        else:
            print("ERROR")
        return redirect(url_for('t_order'))
    print("NE POST")
    return redirect(url_for("t_order"))

@app.route('/orderDenied/<int:order_id>', methods=["POST", "GET"])
def orderDenied(order_id):
    if request.method == "POST":
        db.delOrder(order_id)
        return redirect(url_for('t_order'))
    return redirect(url_for('home'))


@app.route('/changeOrder/<int:order_id>', methods=['POST', 'GET'])
def changeOrder(order_id):
    form = TableOrderForm()
    information = {"info": db.getQuery('table_order', 't_order_id', order_id, t_order_date = "", t_order_time = "", t_order_fio = "", t_order_nop="", t_order_email="")}
    print(information["info"])
    if request.method == "POST":
        print('POST')
        res = db.updateQuery('table_order', 't_order_id', order_id, t_order_date = form.t_order_date.data, t_order_time = form.t_order_time.data, t_order_fio = form.t_order_fio.data,
                            t_order_nop=form.t_order_nop.data, t_order_email = form.email.data)
        if res:
            flash("Данные обновленны")
            return redirect(url_for('t_order'))
        else:
            flash("ERROR")
    print("GET")
    return render_template("changeOrder.html", form=form, information = information, order_id=order_id)


@app.route('/insertRest/<int:event_id>', methods=["POST", "GET"])
def insertRest(event_id):
    form = CreateRest()
    if request.method =="POST":
        db.setRest(event_id=event_id, restoraunt_type = form.r_type.data, restoraunt_name =form.r_name.data, scheldue = form.r_scheldue.data, 
                    rating = form.r_rating.data, adress = form.r_adress.data, contact_number = form.r_contact.data,
                    restoraunt_site = form.r_site.data)
        return redirect(url_for('bar', event_id = event_id))
    return render_template('rInsert.html', form = form)


@app.route('/deleteRest/<int:r_id>/<int:event_id>', methods=["POST", "GET"])
def deleteRest(r_id, event_id):
    if request.method == "POST":
        db.deleteRest(r_id)
        return redirect(url_for("bar", event_id = event_id))
    return redirect(url_for('home'))


@app.route('/updateRest/<int:event_id>/<int:r_id>', methods=["POST", "GET"])
def updateRest(event_id, r_id):
    form = ChangeRest()
    information = {"info": db.getRest(r_id, event_id="", restoraunt_type = "", restoraunt_name ="", scheldue = "", 
                    rating = "", adress = "", contact_number = "", restoraunt_site = "")}
    if request.method == "POST":
        res = db.updateRest(r_id, event_id=event_id, restoraunt_type = form.r_type.data, restoraunt_name =form.r_name.data, scheldue = form.r_scheldue.data, 
                    rating = form.r_rating.data, adress = form.r_adress.data, contact_number = form.r_contact.data,
                    restoraunt_site = form.r_site.data)
        if not res:
            flash("Данные обновленны")
            return redirect(url_for("bar",  event_id=event_id))
        else:
            flash("ERROR")
    return render_template("rUpdate.html", form=form, information = information)


@app.route('/restorauntInfo/<int:r_id>/<int:views>/<restoraunt_name>/<int:free_tables>', methods=["POST", "GET"])
def rInfo(r_id, views, restoraunt_name, free_tables):
    db.plusTable(r_id)
    sort = 0
    form = SearchForm()
    views += 1
    db.updateViews(r_id, views)
    if request.method == "POST":
        if request.form.get("submit") == "submit":
            information = {"menu": db.searchingRMenu(form.search.data, r_id, r_menu_id="", dish_name="", dish_price="", cooking_time="", dish_description="", dish_type=""),
                            "events":db.rEvents(r_id, r_event_id="", r_event_name="", r_event_day="", r_event_time="", r_event_description="")}
            if information["menu"] == False:
                flash('Такого блюда нету!')
                information["menu"] = db.rMenu(sort, r_id, r_menu_id="", dish_name="", dish_price="", cooking_time="", dish_description="", dish_type="")
                return render_template('rInfo.html', information = information, views = views, r_id = r_id, form = form, restoraunt_name = restoraunt_name, free_tables = free_tables)
            flash('Успешно')
            return render_template('rInfo.html', information = information, views = views, r_id = r_id, form = form, restoraunt_name = restoraunt_name, free_tables = free_tables)

        elif request.form.get("price") == "TopPrice":
            sort = 2
            information = {"menu": db.rMenu(sort, r_id, r_menu_id="", dish_name="", dish_price="", cooking_time="", dish_description="", dish_type=""),
                    "events":db.rEvents(r_id, r_event_id="", r_event_name="", r_event_day="", r_event_time="", r_event_description="")}
            return render_template('rInfo.html', information = information, views = views, r_id = r_id, form = form, restoraunt_name = restoraunt_name, free_tables = free_tables)
        
        elif request.form.get("price") == "BottomPrice":
            sort = 1
            information = {"menu": db.rMenu(sort, r_id, r_menu_id="", dish_name="", dish_price="", cooking_time="", dish_description="", dish_type=""),
                    "events":db.rEvents(r_id, r_event_id="", r_event_name="", r_event_day="", r_event_time="", r_event_description="")}
            return render_template('rInfo.html', information = information, views = views, r_id = r_id, form = form, restoraunt_name = restoraunt_name, free_tables = free_tables)
            
        elif request.form.get("time") == "TopTime":
            sort = 3
            information = {"menu": db.rMenu(sort, r_id, r_menu_id="", dish_name="", dish_price="", cooking_time="", dish_description="", dish_type=""),
                    "events":db.rEvents(r_id, r_event_id="", r_event_name="", r_event_day="", r_event_time="", r_event_description="")}
            return render_template('rInfo.html', information = information, views = views, r_id = r_id, form = form, restoraunt_name = restoraunt_name, free_tables = free_tables)
        
        elif request.form.get("time") == "BottomTime":
            sort = 4
            information = {"menu": db.rMenu(sort, r_id, r_menu_id="", dish_name="", dish_price="", cooking_time="", dish_description="", dish_type=""),
                    "events":db.rEvents(r_id, r_event_id="", r_event_name="", r_event_day="", r_event_time="", r_event_description="")}
            return render_template('rInfo.html', information = information, views = views, r_id = r_id, form = form, restoraunt_name = restoraunt_name, free_tables = free_tables)
        
    information = {"menu": db.rMenu(sort, r_id, r_menu_id="", dish_name="", dish_price="", cooking_time="", dish_description="", dish_type=""),
                    "events":db.rEvents(r_id, r_event_id="", r_event_name="", r_event_day="", r_event_time="", r_event_description="")}
    return render_template('rInfo.html', information = information, views = views, r_id = r_id, form = form, restoraunt_name = restoraunt_name, free_tables = free_tables)


@app.route('/insertREvent/<int:r_id>/<int:views>/<int:free_tables>/<restoraunt_name>', methods=["POST", "GET"])
def insertREvent(r_id, views, free_tables, restoraunt_name):
    form = InsertREvent()
    if request.method == "POST":
        db.setQuery("r_events", r_event_name = form.r_event_name.data, r_event_day =form.r_event_day.data, r_event_time = form.r_event_time.data, 
                    r_event_description = form.r_event_description.data, r_id = r_id)
        return redirect(url_for('rInfo', r_id = r_id, views = views, restoraunt_name = restoraunt_name, free_tables = free_tables))
    return render_template('rInsertEvents.html', form = form)


@app.route('/deleteREvent/<int:r_event_id>/<int:r_id>/<int:views>/<int:free_tables>/<restoraunt_name>', methods=["POST", "GET"])
def deleteREvent(r_event_id, r_id, views, free_tables, restoraunt_name):
    if request.method == "POST":
        db.deleteQuery("r_events", "r_event_id", r_event_id)
        return redirect(url_for("rInfo", r_id = r_id, views = views, restoraunt_name = restoraunt_name, free_tables = free_tables))
    return redirect(url_for('home'))


@app.route('/updateREvent/<int:r_event_id>/<int:r_id>/<int:views>/<int:free_tables>/<restoraunt_name>', methods=["POST", "GET"])
def updateREvent(r_event_id, r_id, views, free_tables, restoraunt_name):
    form = UpdateREvent()
    information = {"info": db.getQuery("r_events","r_event_id", r_event_id, r_event_name="", r_event_day= "", r_event_time= "", r_event_description = "")}
    if request.method == "POST":
        res = db.updateQuery("r_events","r_event_id", r_event_id, r_event_name = form.r_event_name.data, r_event_day =form.r_event_day.data, r_event_time = form.r_event_time.data, 
                    r_event_description = form.r_event_description.data, r_id = r_id)
        if not res:
            flash("Данные обновленны")
            return redirect(url_for("rInfo", r_id = r_id, views = views, restoraunt_name = restoraunt_name, free_tables = free_tables))
        else:
            flash("ERROR")
    return render_template("rUpdateEvent.html", form=form, information = information)


@app.route('/insertRMenu/<int:r_id>/<int:views>/<int:free_tables>/<restoraunt_name>', methods=["POST", "GET"])
def insertRMenu(r_id, views, free_tables, restoraunt_name):
    form = CreateRMenu()
    if request.method == "POST":
        db.setQuery("restoraunt_menu", dish_name = form.dish_name.data, dish_price =form.dish_price.data, 
                    cooking_time = form.cooking_time.data, dish_description=form.dish_description.data, r_id = r_id, dish_type=form.dish_type.data)
        return redirect(url_for('rInfo', r_id = r_id, views = views, restoraunt_name = restoraunt_name, free_tables = free_tables))
    return render_template('rInsertMenu.html', form = form)


@app.route('/deleteRMenu/<int:r_menu_id>/<int:r_id>/<int:views>/<int:free_tables>/<restoraunt_name>', methods=["POST", "GET"])
def deleteRMenu(r_menu_id, r_id, views, free_tables, restoraunt_name):
    if request.method == "POST":
        db.deleteQuery("restoraunt_menu", "r_menu_id", r_menu_id)
        return redirect(url_for("rInfo", r_id = r_id, views = views, restoraunt_name = restoraunt_name, free_tables = free_tables))
    return redirect(url_for('home'))


@app.route('/updateRMenu/<int:r_menu_id>/<int:r_id>/<int:views>/<int:free_tables>/<restoraunt_name>', methods=["POST", "GET"])
def updateRMenu(r_menu_id, r_id, views, free_tables, restoraunt_name):
    form = UpdateRMenu()
    information = {"info": db.getQuery("restoraunt_menu","r_menu_id", r_menu_id, dish_name = "", dish_price = "", 
                    cooking_time = "", dish_description="", dish_type="")}
    if request.method == "POST":
        print('POST')
        res = db.updateQuery("restoraunt_menu","r_menu_id", r_menu_id, dish_name = form.dish_name.data, dish_price =form.dish_price.data, 
                    cooking_time = form.cooking_time.data, dish_description=form.dish_description.data, r_id = r_id, dish_type=form.dish_type.data)
        if not res:
            flash("Данные обновленны")
            return redirect(url_for("rInfo", r_id = r_id, views = views, restoraunt_name = restoraunt_name, free_tables = free_tables))
        else:
            flash("ERROR")
    print("GET")
    return render_template("rUpdateMenu.html", form=form, information = information, r_menu_id = r_menu_id, r_id = r_id)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.getUserByEmail(form.email.data, id="", name="", password = "", email="", phone="", picture="", adress="", events="", status="")
        if user and check_password_hash(user['password'], form.password.data):
            if user['status'] == 'admin':
                session['status'] = 'admin'
                session['admin_mode'] = False
            else:
                session['status'] = 'user'
            session['logged_in'] = True
            session['user_id'] = user['id']
            userlogin = Userlogin().create(user)
            login_user(userlogin)
            return redirect(url_for("home"))
        
        
        flash("Неверный логин или пароль!")
    return render_template("login.html", form = form)


@app.route("/logout")
@login_required
def logout():
    session['logged_in'] = False
    session['user_id'] = 0
    session['admin_mode'] = False
    logout_user()
    return redirect(url_for('login'))


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if request.method == "POST":
        hash = generate_password_hash(form.password.data)
        res = db.InsertUser(name = form.name.data, password = hash, email = form.email.data, phone = form.phone.data)
        if res is None:
            flash("Вы успешно зарегестрированны")
            return redirect(url_for("login"))
        else:
            flash("Ошибка при регистрации")
    return render_template("register.html", form=form)


@app.route("/userpage", methods=["POST", "GET"])
@login_required
def userPage():
    if request.method == "POST":
        if request.form.get('admin_mode') == 'admin_on':
            session['admin_mode'] = True
        else:
            session['admin_mode'] = False
    return render_template("userpage.html", name = current_user.get_name(), adress = current_user.get_adress(), 
                            email = current_user.get_email(), phone = current_user.get_phone(), events = current_user.get_events(), status = current_user.get_status())


@app.route("/userava")
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        print("NO IMAGE")
        return ""
    
    h = make_response(img)
    h.headers['Content-Type'] = "image/png"
    return h


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.filename
                file_path = "app/static/avas/" + img
                file.save(file_path)
                res = db.updateUserAvatar(img, current_user.get_id())
                if not res:
                    return redirect(url_for('userPage'))
            except FileNotFoundError as e:
                flash("ERROR")
        else:
            flash("ERROR")
        
        return redirect(url_for('userPage'))


@app.route('/update', methods=["POST", "GET"])
@login_required
def update():
    form = ChangeForm()
    if form.validate_on_submit():
        res = db.updateUser(current_user.get_id(), name = form.name.data, email = form.email.data, phone = form.phone.data, adress = form.adress.data,
                            events = form.events.data)
        if not res:
            flash("Данные обновленны")
            return redirect(url_for("userPage"))
        else:
            flash("ERROR")
    return render_template("userChange.html", form = form, name = current_user.get_name(), 
                            adress = current_user.get_adress(), email = current_user.get_email(), 
                            phone = current_user.get_phone(), events = current_user.get_events())


@app.route('/addToCart<name>/<price>/<int:id>/<page>/<int:event_id>', methods=["POST", "GET"])
def addToCart(name, price, id, page, event_id):
    if request.method == "GET":
        if not session.get('cart'):
            session['cart'] = []
            session['count'] = 0
            session['all_price'] = 0

        session['cart'] += [{
            'product_id': id,
            'product_name': name,
            'product_price': price
        }]
        
        session['count'] += 1
        session['all_price'] += float(price)
        

        flash("Добавлено в корзину")
        print(session["cart"])
    if page == "packs":
        return redirect(url_for("packsPage", event_id = event_id))
    else:
        return redirect(url_for(page))

@app.route('/cart', methods=['POST', 'GET'])
def cart():
    if not session.get('user_id'):
        session['user_id'] = 0
    form = CartForm()
    session['check_cart'] = True
    if not session.get('cart'):
        session['check_cart'] = False
        return render_template("cart.html", form=form, cart_check = session['check_cart'], cart="")
    
    
    if request.method == "POST":
        print("ЗАКАЗ")
        order = ""
        for elem in session['cart']:
            order += elem['product_name'] + ', '
            
        
        if session['user_id'] == 0:
            res = db.setOrder(person_name=form.name.data, person_surname=form.surname.data, person_phone=form.phone.data,
                            person_adress=form.adress.data, person_email=form.email.data, person_town=form.town.data, 
                            person_payment=form.payment.data, person_id=session['user_id'], 
                            last_order=datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                            order_text=order, order_price=session['all_price'])
            if res is None:
                flash("Заказ успешно оформлен")
                session['cart'] = []
                session['count'] = 0
                session['all_price'] = 0
                return redirect(url_for('orderPage'))
            else:
                flash('ERROR')
        else:
            res = db.setOrder(person_name=current_user.get_name(), person_surname=form.surname.data, person_phone=current_user.get_phone(),
                            person_adress=form.adress.data, person_email=current_user.get_email(), person_town=form.town.data, 
                            person_payment=form.payment.data, person_id=session['user_id'],
                            last_order=datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                            order_text=order, order_price=session['all_price'])
            if res is None:
                flash("Заказ успешно оформлен")
                session['cart'] = []
                session['count'] = 0
                session['all_price'] = 0
                return redirect(url_for('orderPage'))
            else:
                flash('ERROR')
        
    
    print('NE ZAKAZ IZ CART')
    information = {
        'cart': session['cart'],
        'count': session['count'],
        'all_price': session['all_price']
    }
    return render_template("cart.html", form=form, cart_check = session['check_cart'], cart = information)


@app.route('/delite_from_cart/<int:id>/<price>', methods=["POST", "GET"])
def delite_from_cart(id, price):
    form = CartForm()
    session['new_cart'] = []
    if request.method == "GET":
        for pr in session['cart']:
            if pr['product_id'] == id:
                pr.clear()
                for elem in range(len(session['cart'])):
                    if session['cart'][elem] == {}:
                        continue
                    session['new_cart'] += [session['cart'][elem]]
                session['cart'] = session['new_cart']
                session['count'] -= 1
                session['all_price'] -= float(price)
                break
        
        if not session.get('cart'):
            session['cart_check'] = False
        else:
            session['cart_check'] = True
        
        information = {
            'cart': session['cart'],
            'count': session['count'],
            'all_price': session['all_price']
        }    
        return render_template("cart.html", form = form, cart = information, cart_check = session['cart_check'])
    
    information = {
            'cart': session['cart'],
            'count': session['count'],
            'all_price': session['all_price']
        }
    return render_template("cart.html", form=form, cart = information, cart_check = session['cart_check'])


@app.route('/orederPage', methods=["POST", "GET"])
def orderPage():
    if not session.get('user_id'):
        session['user_id'] = 0;
    information = { "orders": db.getOrders(session['user_id'], person_name="", person_surname="", person_phone="",
                            person_adress="", person_email="", person_town="", person_payment="", last_order="", order_text="", order_price="", delivery_time="")}
    
    current_time = datetime.fromtimestamp(time.time())
    orders_time = []
    for elem in information['orders']:
        order_time = datetime.strptime(elem['last_order'], '%Y-%m-%d %H:%M:%S')
        new_order_datetime = order_time + timedelta(minutes=20)
        orders_time.append(new_order_datetime)
    
    time_differenses= []
    for elem in orders_time:
        # time_ord = elem.strftime('%Y-%m-%d %H:%M:%S')
        time_dif = elem - current_time
        if  time_dif > timedelta(0):
            minutes_left = int(time_dif.total_seconds() / 60)
            time_differenses.append(f"Осталось {minutes_left} минут")
        else:
            time_differenses.append("Заказ доставлен!")
    
    for elem in information["orders"]:
        elem['delivery'] = time_differenses.pop(0)
    
    
    return render_template('orders.html', orders = information)


@app.route('/statistics', methods=["POST", "GET"])
def statistics():
    form = Checker()
    if request.method == 'POST':
        information = {'info': db.aboutOrders(id="", name="", phone="", adress="", email="", status="")}
        info = information["info"]
        clients = []
        orders = []
        for elem in info:
            clients.append(elem["name"])
            orders.append(elem["order_counter"])

        return render_template("adminInfo.html", information = information, form = form, clients = clients, orders = orders)
    
    
    information = {'info': db.aboutOrders(id="", name="", phone="", adress="", email="", status="")}
    info = information["info"]
    clients = []
    orders = []
    for elem in info:
        clients.append(elem["name"])
        orders.append(elem["order_counter"])

    return render_template("adminInfo.html", information = information, form = form, clients = clients, orders = orders)


@app.route('/setAdmin/<int:user_id>/<name>/<status>', methods=["POST", "GET"])
def setAdmin(user_id, name, status):
    form = Checker()
    if request.method == "POST":
        if form.checker.data and status == 'user':
            db.setAdmin(user_id)
            flash(f"Пользователю {name} присвоен статус admin")
            return redirect(url_for('statistics'))
        elif not form.checker.data and status == 'admin':
            db.setUser(user_id)
            flash(f"Администратору {name} присвоен статус user")
            return redirect(url_for('statistics'))
    return redirect(url_for('statistics'))


@app.route("/sendVerify", methods=["POST", "GET"])
def sendVerify():
    form = SendVerify()
    if form.validate_on_submit():
        verify = Verify(form.email.data)
        verify_number = verify.verify()
        return redirect(url_for('forgotPassword', verify_number=verify_number, email = form.email.data))
    return render_template('sendVerify.html', form = form)


@app.route('/forgotPassword/<int:verify_number>/<email>', methods=["POST", "GET"])
def forgotPassword(verify_number, email):
    form = ForgottenPassword()
    if form.validate_on_submit():
        if int(form.verify.data) == verify_number:
            hash = generate_password_hash(form.new_password.data)
            if check_password_hash(hash, form.repeat.data):
                res = db.updatePassword(email, hash)
                flash("Пароль обновлён!")
                return redirect(url_for("login"))
            else:
                flash("Пароли не совподают")
                return redirect(url_for('forgotPassword', verify_number = verify_number, email = email))
        else:
            flash("Неверный проверочный код!")
            return redirect(url_for('forgotPassword', verify_number = verify_number, email = email))
    return render_template('forgotPassword.html', form = form)


@app.route('/sendCheck/<name>/<surname>/<email>/<float:total>/<order>/<delivery>', methods=["POST", "GET"])
def sendCheck(name, surname, email, total, order, delivery):
    if request.method == "POST":
        create = CreateCheck(name=name, surname=surname, total=total, order=order, delivery=delivery )
        create.createCheckForPack()
        if create:
            print("EXELENT")
        else:
            print("ERROR")
        send = SendCheck(email)
        send.sendCheck()
        if send:
            print("EXELENT")
        else:
            print("ERROR")
        return redirect(url_for('orderPage'))
    print("NE POST")
    return redirect(url_for("orderPage"))


@app.route('/placeStatistic', methods=["POST", "GET"])
def placeStatistic():
    information = {"info": db.selectViews(restoraunt_name="", r_views="")}
    info = information["info"]
    restoraunt = []
    views = []
    for elem in info:
        restoraunt.append(elem["restoraunt_name"])
        views.append(elem["r_views"])
    
    return render_template('placeStatistic.html', information = information, restoraunt = restoraunt, views = views)


@app.route('/eventStatistic', methods=["POST","GET"])
def eventStatistic():
    information = {"info": db.selectViewsEvent(type_of_event="", view_count="")}
    info = information["info"]
    type = []
    views = []
    for elem in info:
        type.append(elem["type_of_event"])
        views.append(elem["view_count"])
    
    return render_template('eventStatistic.html', information = information, type = type, views = views)


@app.route("/download_json")
def download_json():
    filepath = db.json()
    full_path = "jsonfiles/" + filepath
    return send_file(full_path, as_attachment=True, download_name='example.json', mimetype='application/json')


@app.route("/orderStatistic/<int:user_id>", methods=["POST", "GET"])
def orderStatistic(user_id):
    information = {"opack": db.getOrders(user_id, order_id="", person_name="", person_surname="", person_phone="",
                            person_adress="", person_email="", person_town="", person_payment="", last_order="", order_text="", order_price="", delivery_time=""),
                    "otable": db.getTOrders(user_id, t_order_id="", t_order_date="", t_order_time="", t_order_fio = "",
                                t_order_nop="", t_order_rname = "", t_order_email="")}
    current_time = datetime.fromtimestamp(time.time())
    orders_time = []
    for elem in information['opack']:
        order_time = datetime.strptime(elem['last_order'], '%Y-%m-%d %H:%M:%S')
        new_order_datetime = order_time + timedelta(minutes=20)
        orders_time.append(new_order_datetime)
    
    time_differenses= []
    for elem in orders_time:
        # time_ord = elem.strftime('%Y-%m-%d %H:%M:%S')
        time_dif = elem - current_time
        if  time_dif > timedelta(0):
            minutes_left = int(time_dif.total_seconds() / 60)
            time_differenses.append(f"Осталось {minutes_left} минут")
        else:
            time_differenses.append("Заказ доставлен!")
    
    for elem in information["opack"]:
        elem['delivery'] = time_differenses.pop(0)
    return render_template('allOrders.html', information = information, user_id = user_id)


@app.route('/orderDelete/<int:order_id>/<int:user_id>', methods=["POST", "GET"])
def orderDelete(order_id, user_id):
    if request.method == "POST":
        db.delOrder(order_id)
        return redirect(url_for('orderStatistic', user_id = user_id))
    return redirect(url_for('home'))


@app.route('/changeStatOrder/<int:order_id>/<int:user_id>', methods=['POST', 'GET'])
def changeStatOrder(order_id, user_id):
    form = TableOrderForm()
    if request.method == "POST":
        print('POST')
        res = db.updateQuery('table_order', 't_order_id', order_id, t_order_date = form.t_order_date.data, t_order_time = form.t_order_time.data, t_order_fio = form.t_order_fio.data,
                            t_order_nop=form.t_order_nop.data, t_order_email = form.email.data)
        if res:
            flash("Данные обновленны")
            return redirect(url_for('orderStatistic', user_id = user_id))
        else:
            flash("ERROR")
    print("GET")
    information = {"info": db.getQuery('table_order', 't_order_id', order_id, t_order_date = "", t_order_time = "", t_order_fio = "", t_order_nop="", t_order_email="")}
    return render_template("changeStatOrder.html", form=form, information = information, order_id=order_id, user_id = user_id)


@app.route('/changeStatPOrder/<int:order_id>/<int:user_id>', methods=["POST", "GET"])
def changeStatPOrder(order_id, user_id):
    form = CartChangeForm()
    if request.method == "POST":
        print('POST')
        res = db.updateQuery('person_order', 'order_id', order_id,  person_name=form.name.data, person_surname=form.surname.data, person_phone=form.phone.data,
                            person_adress=form.adress.data, person_email=form.email.data, person_town=form.town.data, person_payment=form.payment.data, order_text=form.order_text.data, order_price=form.price.data)
        if res:
            flash("Данные обновленны")
            return redirect(url_for('orderStatistic', user_id = user_id))
        else:
            flash("ERROR")
    print('GET')
    information = {"info": db.getQuery('person_order', 'order_id', order_id, person_name="", person_surname="", person_phone="",
                            person_adress="", person_email="", person_town="", person_payment="", last_order="", order_text="", order_price="", delivery_time="")}
    return render_template('changeStatPOrder.html', form = form, information = information)

@app.route('/sendStatTCheck/<fio>/<date>/<time>/<int:nop>/<rname>/<email>/<int:user_id>', methods=["POST", "GET"])
def sendStatTCheck(fio, date, time, nop, rname, email, user_id):
    if request.method == "POST":
        create = CreateCheck(fio=fio, date=date, time=time, nop=nop, rname = rname)
        create.createCheckForTable()
        if create:
            print("EXELENT")
        else:
            print("ERROR")
        send = SendCheck(email)
        send.sendCheck()
        if send:
            print("EXELENT")
        else:
            print("ERROR")
        return redirect(url_for('orderStatistic', user_id = user_id))
    print("NE POST")
    return redirect(url_for('orderStatistic', user_id = user_id))


@app.route('/sendStatCheck/<name>/<surname>/<email>/<float:total>/<order>/<delivery>/<int:user_id>', methods=["POST", "GET"])
def sendStatCheck(name, surname, email, total, order, delivery, user_id):
    if request.method == "POST":
        create = CreateCheck(name=name, surname=surname, total=total, order=order, delivery=delivery )
        create.createCheckForPack()
        if create:
            print("EXELENT")
        else:
            print("ERROR")
        send = SendCheck(email)
        send.sendCheck()
        if send:
            print("EXELENT")
        else:
            print("ERROR")
        return redirect(url_for('orderStatistic', user_id = user_id))
    print("NE POST")
    return redirect(url_for('orderStatistic', user_id = user_id))


@app.route('/delStatPOrder/<int:order_id>/<int:user_id>', methods=["POST", "GET"])
def delStatPOrder(order_id, user_id):
    if request.method == "POST":
        db.deleteQuery("person_order", "order_id", order_id)
        return redirect(url_for('orderStatistic', user_id = user_id))
    return redirect(url_for('home'))


@app.route('/exelImport', methods=['POST', 'GET'])
def exelImport():
    res = db.getUserForExel(id="", name="", password = "", email="", phone="", picture="", adress="", events="", status="")
    output = BytesIO()

    # Экспорт данных в Excel и запись в BytesIO
    res.to_excel(output, sheet_name='Sheet1', index=False, engine='xlsxwriter')

    # Устанавливаем указатель BytesIO в начало
    output.seek(0)

    # Отправляем файл пользователю
    return send_file(output, download_name='data.xlsx', as_attachment=True)


@app.route('/savePackJSON/<int:event_id>', methods=["POST", "GET"])
def save_pack_json(event_id):
    form = AddPackJSON()
    if form.validate_on_submit():
        pack_data = {
            'pack_name': form.pack_name.data,
            'pack_type': form.pack_type.data,
            'pack_fillin': form.pack_fillin.data,
            'pack_price': form.pack_price.data,  # Преобразование Decimal в float
            'number_of_people': form.number_of_people.data,
            'pack_description': form.pack_description.data,
            'event_id': event_id 
        }

        # Создание временного файла для сохранения JSON
        temp_file_path = os.path.join(tempfile.gettempdir(), 'pack_data.json')
        with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
            json.dump(pack_data, temp_file, ensure_ascii=False)

        send_file(temp_file_path, as_attachment=True, download_name='employees_data.json')
        
        # db.setPack(pack_name=form.pack_name.data, pack_type = form.pack_type.data, pack_fillin = form.pack_fillin.data, pack_price = form.pack_price.data,
        #     number_of_people = form.number_of_people.data, pack_description = form.pack_description.data, event_id = event_id)
        return send_file(temp_file_path, as_attachment=True, download_name='employees_data.json')
    return render_template('AddPackJSON.html', form = form)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploadJSON', methods=['POST'])
def uploadJSON():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = app.config['UPLOAD_FOLDER'] + '/' + filename
        file.save(file_path)

        # Импорт данных в PostgreSQL
        try:
            db.import_json_to_postgres(file_path, 'packs')
            return 'Файл успешно загружен и импортирован в базу данных.'
        except ValueError as e:
            return f'Ошибка: {str(e)}'

    return 'Недопустимый тип файла.'





if __name__ == "__main__":
    app.run(debug="True")
