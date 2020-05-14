# -*- coding: utf-8 -*-
import kivy
import os
import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
#Parametros de la pantalla
from kivy.config import Config
Config.set("graphics","width","340")
Config.set("graphics","height","640")

#Conexión de la base de datos
def connect_to_database(path):
    try:
        con = sqlite3.connect(path)
        cursor = con.cursor()
        create_table_productos(cursor)
        con.commit()
        con.close()
    except Exception as e:
        print(e)

#Creación de la tabla productos
def create_table_productos(cursor):
    cursor.execute(
        """
        CREATE TABLE Productos(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombre TEXT NOT NULL,
        Marca TEXT NOT NULL,
        Precio FLOAT NOT NULL,
        Stock INT NOT NULL,
        Caducidad DATE NOT NULL
        )
        """
    )

class MessagePopup(Popup):
    pass

class MainWid(ScreenManager):
    def __init__(self, **kwargs): #recibe un diccionario de parametros
        super(MainWid, self).__init__()
        self.APP_PATH = os.getcwd() #constante DB
        self.DB_PATH = self.APP_PATH + "/my_database.db"
        self.StartWid = StartWid(self) #instancia de la clase StartWid
        self.DataBaseWid = DataBaseWid(self)
        self.InsertDataWid = BoxLayout()#Limpiar para inicar nuevo widget %%%%%
        self.UpdateDataWid = BoxLayout() #Actualizar producto
        self.Popup = MessagePopup()

        wid = Screen(name="start")
        wid.add_widget(self.StartWid)
        self.add_widget(wid)
        wid = Screen(name="database")
        wid.add_widget(self.DataBaseWid)
        self.add_widget(wid)
        #%%%%%
        wid = Screen(name="insertdata")
        wid.add_widget(self.InsertDataWid)
        self.add_widget(wid)
        wid = Screen(name="updatedata")
        wid.add_widget(self.UpdateDataWid)
        self.add_widget(wid)

    #Función que ayuda a acomodar las pantallas en el momento que se invoquen.
        self.goto_start()
    def goto_start(self):
        self.current = "start"

    def goto_database(self):
        self.DataBaseWid.check_memory()
        self.current = "database"

    #%%%%%
    def goto_insertdata(self):
        self.InsertDataWid.clear_widgets()#para limpiarlo
        wid = InsertDataWid(self)
        self.InsertDataWid.add_widget(wid)
        self.current = "insertdata"

    def goto_updatedata(self,data_id):
        self.UpdateDataWid.clear_widgets()#para limpiarlo
        wid = UpdateDataWid(self,data_id)
        self.UpdateDataWid.add_widget(wid)
        self.current = "updatedata"

#Pantalla inicial
class StartWid(BoxLayout):
    def __init__(self,mainwid,**kwargs):
        super(StartWid, self).__init__()
        self.mainwid = mainwid

    def create_database(self):
        connect_to_database(self.mainwid.DB_PATH)
        self.mainwid.goto_database()

#clase que contiene todo lo de la DB y el boton agregar
class DataBaseWid(BoxLayout):
    def __init__(self,mainwid,**kwargs):
        super(DataBaseWid,self).__init__()
        self.mainwid = mainwid

    #Agegar el boton al final de cada widget (refrescar)
    def check_memory(self):
        self.ids.container.clear_widgets()
        #para la tarjeta editar
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        cursor.execute('SELECT ID, Nombre, Marca, Precio, Stock, Caducidad FROM Productos')
        for i in cursor:
            wid = DataWid(self.mainwid)
            r1 = 'ID: '+str(100000000+i[0])[1:9]+'\n'
            r2 = i[1]+', '+i[2]+'\n'
            r3 = 'Precio por unidad: $'+str(i[3])+'\n'
            r4 = 'En stock: '+str(i[4])+'\n'
            r5 = 'Caducidad: '+str(+i[5])
            wid.data_id = str(i[0])
            wid.data = r1+r2+r3+r4+r5
            self.ids.container.add_widget(wid)
        #hasta aqui
        wid = NewDataButton(self.mainwid)
        self.ids.container.add_widget(wid)
        con.close()

#Clase para agregar productos, formulario
class InsertDataWid(BoxLayout):
    def __init__(self,mainwid,**kwargs):
        super(InsertDataWid,self).__init__()
        self.mainwid = mainwid

    def insert_data(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        #d1 = self.ids.ti_id.text
        d2 = self.ids.ti_nombre.text
        d3 = self.ids.ti_marca.text
        d4 = self.ids.ti_precio.text
        d5 = self.ids.ti_stock.text
        d6 = self.ids.ti_caducidad.text
        a1 = (d2,d3,d4,d5,d6)
        s1 = 'INSERT INTO Productos(ID, Nombre, Marca, Precio, Stock, Caducidad)'
        s2 = 'VALUES(null,"%s","%s","%s","%s",%s)' % a1

        try:
            cursor.execute(s1+' '+s2)
            con.commit()
            con.close()
            self.mainwid.goto_database()
        except Exception as e:
            message = self.mainwid.Popup.ids.message
            self.mainwid.Popup.open()
            self.mainwid.Popup.title = "Data base error"
            if '' in a1:
                message.text = "Uno o más campos están vacíos"
            else:
                message.text = str(e)
            con.close()

    def back_to_dbw(self):
        self.mainwid.goto_database()

class UpdateDataWid(BoxLayout):
    def __init__(self, mainwid, data_id, **kwargs):
        super(UpdateDataWid, self).__init__()
        self.mainwid = mainwid
        self.data_id = data_id
        self.check_memory()

    def check_memory(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        s = 'SELECT Nombre, Marca, Precio, Stock, Caducidad FROM Productos WHERE ID='
        cursor.execute(s+self.data_id)
        for i in cursor:
            self.ids.ti_nombre.text = i[0]
            self.ids.ti_marca.text = i[1]
            self.ids.ti_precio.text = str(i[2])
            self.ids.ti_stock.text = str(i[3])
            self.ids.ti_caducidad.text = str(i[4])
        con.close()
    def update_data(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        d1 = self.ids.ti_nombre.text
        d2 = self.ids.ti_marca.text
        d3 = self.ids.ti_precio.text
        d4 = self.ids.ti_stock.text
        d5 = self.ids.ti_caducidad.text
        a1 = (d1, d2, d3, d4, d5)
        s1 = 'UPDATE Productos SET'
        s2 = 'Nombre="%s",Marca="%s",Precio=%s,Stock=%s,Caducidad=%s'% a1
        s3 = 'WHERE ID=%s' % self.data_id

        try:
            cursor.execute(s1 + ' ' + s2+' '+s3)
            con.commit()
            con.close()
            self.mainwid.goto_database()
        except Exception as e:
            message = self.mainwid.Popup.ids.message
            self.mainwid.Popup.open()
            self.mainwid.Popup.title = "Data base error"
            if '' in a1:
                message.text = "Uno o más campos están vacíos"
            else:
                message.text = str(e)
            con.close()
    def delete_data(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        s = 'DELETE FROM Productos WHERE ID='+self.data_id
        cursor.execute(s)
        con.commit()
        con.close()
        self.mainwid.goto_database()
    def back_to_dbw(self):
        self.mainwid.goto_database()

#captura de datos
class DataWid(BoxLayout):
    def __init__(self, mainwid,**kwargs):
        super(DataWid, self).__init__()
        self.mainwid = mainwid

    def update_data(self, data_id):
        self.mainwid.goto_updatedata(data_id)

#Boton que agrega los widgets
class NewDataButton(Button):
    def __init__(self, mainwid, **kwargs):
        super(NewDataButton, self).__init__()
        self.mainwid = mainwid

    def create_new_product(self):
        self.mainwid.goto_insertdata()

class MainApp(App):
    title = "Inventario simple"
    def build(self):
        return MainWid() #Regresa al contenido principal

#Condición
if __name__ == "__main__":
    MainApp().run()