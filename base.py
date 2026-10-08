import turtle
import time
import math
import random
import json 
import os
import datetime
from PIL import Image, ImageTk
from pynput import keyboard
from screeninfo import get_monitors

turtle.colormode(255)  

class App:
    def __init__(self):
        self.Screen = turtle.Screen()
        self.Screen.listen()
        self.Screen.getcanvas().focus_force()
        self.Screen.screensize(800, 1000)#размер полотна
        self.Screen.setup(800, 1000)#размер окна
        self.Screen.bgcolor("black")
        self.Screen.tracer(0)
        self.Screen.delay(0)
        self.Screen.title("kvak")#название окна 
        self.Scenes = Scenes(self)
        self.Ui = Ui(self) 
        self.Screen.onscreenclick(self.click, 1)
        self.renderer = turtle.Turtle()  
        self.renderer.penup()
        self.renderer.hideturtle()
        self.renderer.speed(0)

    def on_press(self, key):
        try:
            key_name = key.char
        except AttributeError:
            key_name = key.name
        if key_name in hotkeys:
            if hotkeys[key_name]() is False:
                return False

    def on_release(self, key):
        try:
            key_name = key.char
        except AttributeError:
            key_name = key.name
        if key_name in hotkeys_release:
            if hotkeys_release[key_name]() is False:
                return False

    def click(self, x, y):
        distances = []
        for button in self.Ui.Buttons.buttons:

            if not button["available"]:
                continue
            match button["shape"]:
                case "circle":
                    dx = x - button["pos"][0]
                    dy = y - button["pos"][1]
                    distances.append(math.sqrt(dx ** 2 + dy ** 2))
                case "rectangle":
                    if (button["pos"][0] - button["size"][0] // 2 < x < button["pos"][0] + button["size"][0] // 2) and (button["pos"][1] - button["size"][1] // 2 < y < button["pos"][1] + button["size"][1] // 2):
                        if button["arg"][0] == False:
                            button["action"]()
                        else:
                            button["action"](button["arg"])
                        return
        if distances == []:
            return               
        nearest = min(distances)
        index = distances.index(nearest)
        if nearest < self.Ui.Buttons.buttons[index]["size"] / 2:
            if self.Ui.Buttons.buttons[index]["arg"][0] == False:
                self.Ui.Buttons.buttons[index]["action"]()
            else:
                button["action"](self.Ui.Buttons.buttons[index]["arg"])

    def update(self):
        self.renderer.clear()
        self.Ui.Frames.render()
        self.Ui.Buttons.render()
        self.Ui.Labels.render()
        self.Screen.update()

    def close(self):
        self.Screen.bye()
        exit()

class Ui:
    def __init__(self, App):
        self.Buttons = Buttons(self)
        self.Labels = Labels(self)
        self.Frames = Frames(self)
        self.App = App

    def hide_group(self, name):
        for button in self.Buttons.buttons:
            if button["group"] == name:
                button["visible"] = False
                button["available"] = False
        for label in self.Labels.labels:
            if label["group"] == name:
                label["visible"] = False
        for frame in self.Frames.frames:
            if frame["group"] == name:
                frame["visible"] = False

    def delete_group(self, name):
        button_names = [b["name"] for b in self.Buttons.buttons if b["group"] == name]
        label_names = [l["name"] for l in self.Labels.labels if l["group"] == name]
        frame_names = [f["name"] for f in self.Frames.frames if f["group"] == name]
        if button_names:
            self.Buttons.delete(*button_names)
        if label_names:
            self.Labels.delete(*label_names)
        if frame_names:
            self.Frames.delete(*frame_names)

    def show_group(self, name):
        for button in self.Buttons.buttons:
            if button["group"] == name:
                button["visible"] = True
                button["available"] = True
        for label in self.Labels.labels:
            if label["group"] == name:
                label["visible"] = True
        for frame in self.Frames.frames:
            if frame["group"] == name:
                frame["visible"] = True

    def hide_all(self):
        for button in self.Buttons.buttons: 
            button["available"] = False 
            button["visible"] = False
        for label in self.Labels.labels:
            label["visible"] = False
        for frame in self.Frames.frames:
            frame["visible"] = False

    def show_all(self):
        for button in self.Buttons.buttons:
            button["available"] = True
            button["visible"] = True
        for label in self.Labels.labels:
            label["visible"] = True
        for frame in self.Frames.frames:
            frame["visible"] = True

    def clear(self):
        self.App.renderer.clear()
        self.Buttons.buttons = []
        self.Labels.labels = []
        self.Frames.frames = []
   
class Labels:
    def __init__(self, Ui):
        self.Ui = Ui
        self.labels = []
    
    def new(self, name, pos, align, text = "", color = "black", font=("Arial", 16, "normal"), group = ""):
        self.labels.append({
            "name": name,
            "pos": pos,
            "align": align,
            "text": text,
            "color": color,
            "font": font,
            "visible": True,
            "group": group
        })

    def get_index(self, name):
        for i, label in enumerate(self.labels):
            if label["name"] == name:
                return i
                       
    def change_value(self, name, key, value):
        for label in self.labels:
            if label["name"] == name:
                label[key] = value

    def delete(self, *names):
        for name in names:
            for i, label in enumerate(self.labels):
                if label["name"] == name:
                    del self.labels[i]

    def render(self):
        for label in self.labels:
            if label["visible"]:
                self.Ui.App.renderer.goto(label["pos"][0], label["pos"][1] - label["font"][1] // 2)
                self.Ui.App.renderer.color(label["color"])
                self.Ui.App.renderer.write(label["text"], align=label["align"], font=label["font"])

class Buttons:
    def __init__(self, Ui):
        self.Ui = Ui
        self.buttons = []

    def new(self, button_name, button_shape, button_size, button_pos, button_action, button_color = "white", 
            border_size = 1, border_color = "black", button_text = "", text_font = ("Arial", 16, "normal"),
            text_color = "black", action_arg = [False], button_available = True, button_visible = True, group = ""):
        
        self.buttons.append({
            "name": button_name,
            "shape": button_shape,
            "size": button_size,
            "pos": button_pos,
            "action": button_action,
            "arg": action_arg,
            "available": button_available,
            "color": button_color,
            "border_size": border_size,
            "border_color": border_color,
            "text": button_text,
            "font": text_font,
            "text_color": text_color,
            "visible": button_visible,
            "group": group
        })

    def get_index(self, name):
        for i, button in enumerate(self.buttons):
            if button["name"] == name:
                return i
            
    def change_value(self, name, key, value):
        for button in self.buttons:
            if button["name"] == name:
                button[key] = value

    def delete(self, *names):
        for name in names:
            for i, button in enumerate(self.buttons):
                if button["name"] == name:
                    del self.buttons[i]

    def render(self):
        for button in self.buttons:
            if not button["visible"]:
                continue
            match button["shape"]:
                case "rectangle":
                    self.Ui.App.renderer.goto(button["pos"][0] - button["size"][0] / 2, button["pos"][1] + button["size"][1] / 2)
                    self.Ui.App.renderer.pendown()
                    self.Ui.App.renderer.color(button["border_color"])
                    self.Ui.App.renderer.pensize(button["border_size"])
                    self.Ui.App.renderer.begin_fill()
                    self.Ui.App.renderer.goto(button["pos"][0] - button["size"][0] / 2, button["pos"][1] - button["size"][1] / 2)
                    self.Ui.App.renderer.goto(button["pos"][0] + button["size"][0] / 2, button["pos"][1] - button["size"][1] / 2)
                    self.Ui.App.renderer.goto(button["pos"][0] + button["size"][0] / 2, button["pos"][1] + button["size"][1] / 2)
                    self.Ui.App.renderer.goto(button["pos"][0] - button["size"][0] / 2, button["pos"][1] + button["size"][1] / 2)
                    self.Ui.App.renderer.color(button["color"])
                    self.Ui.App.renderer.end_fill()
                    self.Ui.App.renderer.penup()
                case "circle":
                    self.Ui.App.renderer.goto(button["pos"][0], button["pos"][1] - button["size"] // 2)
                    self.Ui.App.renderer.pendown()
                    self.Ui.App.renderer.color(button["border_color"])
                    self.Ui.App.renderer.pensize(button["border_size"])
                    self.Ui.App.renderer.begin_fill()
                    self.Ui.App.renderer.circle(button["size"] // 2)
                    self.Ui.App.renderer.color(button["color"])
                    self.Ui.App.renderer.end_fill()
                    self.Ui.App.renderer.penup()
            self.Ui.App.renderer.goto(button["pos"][0], button["pos"][1] - button["font"][1] / 1.3)
            self.Ui.App.renderer.color(button["text_color"])
            self.Ui.App.renderer.write(button["text"], align="center", font=button["font"])

class Frames:
    def __init__(self, Ui):
        self.Ui = Ui
        self.frames = []

    def new(self, name, color, points, iscircle = False, pos=(0, 0), radius = 0, group = "", z_index = 0):
        self.frames.append({
            "name": name,
            "color": color,
            "points": points,
            "iscircle": iscircle,
            "pos": pos,
            "radius": radius,
            "visible": True,
            "group": group,
            "z_index": z_index
        })
        self.z_index_sort()

    def get_index(self, name):
        for i, frame in enumerate(self.frames):
            if frame["name"] == name:
                return i
            
    def change_value(self, name, key, value):
        for frame in self.frames:
            if frame["name"] == name:
                frame[key] = value
                if key == "z_index":
                    self.z_index_sort()

    def delete(self, *names):
        for name in names:
            for i, frame in enumerate(self.frames):
                if frame["name"] == name:
                    del self.frames[i]
                    self.z_index_sort()

    def z_index_sort(self):
        self.frames.sort(key=lambda x: x["z_index"])

    def render(self):
        for frame in self.frames:
            if not frame["visible"]:
                continue
            self.Ui.App.renderer.pensize(1)
            self.Ui.App.renderer.color(frame["color"])
            if frame["iscircle"]:
                self.Ui.App.renderer.goto(frame["pos"][0], frame["pos"][1] - frame["radius"])
                self.Ui.App.renderer.begin_fill()
                self.Ui.App.renderer.pendown()
                self.Ui.App.renderer.circle(frame["radius"])
                self.Ui.App.renderer.end_fill()
                self.Ui.App.renderer.penup()
                return
            self.Ui.App.renderer.goto(frame["points"][0])
            self.Ui.App.renderer.pendown() 
            self.Ui.App.renderer.begin_fill()
            for edge in frame["points"][1:]:
                self.Ui.App.renderer.goto(edge)
            self.Ui.App.renderer.goto(frame["points"][0])
            self.Ui.App.renderer.end_fill()
            self.Ui.App.renderer.penup()                            

class Scenes:

    def __init__(self, App):
        self.App = App

    """Это важный класс в котором разные сцены будут взаимодействовать между собой. 
    Тут я объясню как создать кнопку, фрам, надпись и как создать сценну.
    начнём
    у нас есть 3 вида то чего мы видим на экране это кнопки то на что нажимаем, фрамы типо фонов цветных частей и текст то что читаем.
    и у всех них есть общие методы. Что бы создать что то из этого мы пишем new(аргументы) чтоб удалить delete(название элемента) что бы изменить один параметр change_value(название элемента, название параметра, название нового параметра)
    но не все так просто мы не можем просто написать что то из этого. Для этого мы имеем 1 корневой класс app он все связывает, класс UI групирует элементы экрана и дальше 3 класса для управления каждым из элементов.
    Создание кнопки начаналось бы так:
    
    self.App.Ui.Buttons.new(аргументы)
    
    создание текста или фрама не отличалось бы кроме слова между UI и new. У текста там будет Labels вместо Buttons а для фрама Frame
    страшнее всего узнать какие же аргументы мы будем использовать.. и так начнем:

    def new(self, button_name, button_shape, button_size, button_pos, button_action, button_color = "white", 
                border_size = 1, border_color = "black", button_text = "", text_font = ("Arial", 16, "normal"),
                text_color = "black", action_arg = [False], button_available = True, button_visible = True, group = "")

    Что это? Это функция создания кнопок. Да аргументов много. На self не обращаем внимание. Я не смогу объяснить каждый аргумент лишь поясню что то не понятное и вид аргумента:
    button_pos - позиция центра кнопки. Она указывается так (x, y) да прямо со скобками
    button_shape - форма кнопки. Есть triangle, rectangle(обычная), circle
    button_size - размеры кнопки. так же указываються КВАДРАТНЫХ в скобках вот: [высота, ширина](! если кпопка круглая то просто число, длина радиуса.)
    !button_action! - важная характеристика тут мы пишем название функции которая выполниться при нажатии на кнопку. (без ковычек и круглых скобок)
    
    еще запомни про агрументы, если там с цветом то можно и текстом "black" и rgb кодом но тогда в скобках: (r, g, b)
    
    остальные параметры не обязательны их значение можно понять по названию.
    Если их не указать или указывать не в правельном порядке все будет хорошо но параметры обязательные должны быть и они сохраняют порядок.
    Какие обязательные? те что в начале функции и у них не написанно так: аргумент = "значение" тоесть у них нету базового значения и программа ожидает от вас ввода этого значения обязательно.

    теперь покажем строку создания кнопки уже рабочую строку. Это страшно

    self.App.Ui.Buttons.new(f"more_machine", "rectangle", [size, size], (x, y), self.more_machine, "black", 2, "red", "+", ("Arial", 20, "bold"), "red")

    ладно это не страшная кнопка но есть страшнее. Как видим тут есть название, форма, размер, функция и дальше не обязательные параметры. 
    Заметьте! В этом коде необяз параметры идут по порядку но если тебу нужен один не обяз параметр то не надо писать прошлые можно написать так

    new(обяз аргументы, название не обяз аргумента = значение)

    чтоб лучше понял покажу что такой код:

    self.App.Ui.Buttons.new(f"more_machine", "rectangle", [size, size], (x, y), self.more_machine, button_color = "black", border_size = 2, border_color = "red", button_text = "+", text_font = ("Arial", 20, "bold"), text_color = "red")
    
    тоже сработал бы. Он более читаемый понятный но длинее по этому я выбирал первый вариант. Указывай название аргумента только если он тебе нужен и за ним есть другие не нужные.

    ну вот это все про создание. Расмотри коды создания текста и фрама. Потом я объясню и их

    def new(self, name, pos, align, text = "", color = "black", font=("Arial", 16, "normal"), group = ""): - текст

    def new(self, name, color, points, iscircle = False, pos=(0, 0), radius = 0, group = "", z_index = 0) - фрамы


    Это все отлично но где писать этот код? надо научиться сделать сценны. Чтоб её создать просто напишем в этом классе функцию под названием game_menu
    название должно быть говорящим и оно и говорит что тогда будет на экране
    

    def game_menu():
        pass

    потом прочитав код дальше поймешь почему именно это название и его можно будет изменить
    
    для начала надо очистить экран и это делаеться строкой:
    
    self.App.Ui.clear()
    
    мы удалили все части прошлой сцены
    
    теперь напием код для создания круглой кнопки в центре (координаты 0, 0) радиусом 25 пикселей с красными краями толщиной 5 пикселей, с оранжевым основанием и текстом черного цвета размера 10 пунктов: Нажми!
    наша кнопка будет изменять свой же текст по нажатию на "уро!" с помощью функции change_text() она может быть где угодно но лучше тоже в классе Scenes. И тогда в аргументы на функцию кнопки мы напишем self.change_text
    в классах self обозначает что что то в нём самом тоесть наша функция
    (! название кнопки не бесполезно оно не где не покажеться но поможет изменять параметры опредлелнной кнопки и различать программе кнопки в целом. ! не называй кнопки одинаково)
    
    self.App.Ui.Butons.new("first_button", "circle", 25, (0, 0), self.change_text, button_color = "orange", 
                border_size = 5, border_color = "red", button_text = "Нажми!", text_font = ("Arial", 10, "normal"),
                text_color = "black")

    по скольку все аргументы идут по порядку можно написать без названий. Выглядеть будет вот так:

    self.App.Ui.Butons.new("first_button", "circle", 25, (0, 0), self.change_text, "orange", 
                5, "red", "Нажми!", ("Arial", 10, "normal"), "black")

    мы нарисовали кнопку. Чтоб она была видна в самом конце функции надо бновить экран. С помощью этого:

    self.App.update()

    соберем в кучку:



    def change_text(self):
        pass
        
    def game_menu(self):
        self.App.Ui.clear()

        self.App.Ui.Buttons.new("first_button", "circle", 25, (0, 0), self.change_text, "orange", 
                        5, "red", "Нажми!", ("Arial", 10, "normal"), "black")

        self.App.update()


    Чего то не хватает. Точно функция change text ничего не делает и кнопка бессполезна
    Нам надо изменить тест кнопки значит используем функцию change_value которая поменяет значение параметра, в нашем случае текста на новое.
    выглядеть будет так:

    self.App.Ui.Buttons.change_value("first_buttons", "text", "ура!")

    3 аргумента

    1 - название кнопки!
    2 - название аргумента(может не совпадать с названием аргумента при создании. Например button_text - text)
    чтоб не путаться смотри в код создания кнопки при создании словаря для кнопки и сравнивай.
    вот код полный:

        def new(self, button_name, button_shape, button_size, button_pos, button_action, button_color = "white", 
            border_size = 1, border_color = "black", button_text = "", text_font = ("Arial", 16, "normal"),
            text_color = "black", action_arg = [False], button_available = True, button_visible = True, group = ""):
        
        self.buttons.append({
            "name": button_name,
            "shape": button_shape,
            "size": button_size,
            "pos": button_pos,
            "action": button_action,
            "arg": action_arg,
            "available": button_available,
            "color": button_color,
            "border_size": border_size,
            "border_color": border_color,
            "text": button_text,
            "font": text_font,
            "text_color": text_color,
            "visible": button_visible,
            "group": group
        })

    к примеру button_action - стал action. Это все сокращение и я думаю так легче даже. Нет двойных слов просто text просто action просто name и тд

    3 - новое значение аргумента. Было "нажми" теперь "ура"

    ну все ты понял как создать сценну. (подсказка: ведь кнопке можно передать как функцию другую фукцию сцены и так получаеться переход между сценами)
    и кнопку. 
    чтоб изменить цвет экрана пиши 
    self.App.Screen.bgcolor(цвет)
    и
    self.App.update()
    обновили экран чтоб изменения были видны

    ну а потом еще объясню.
    я устал.
    ква.

    (код который писали в коментарии перенес в сам класс без коментироания и то что мы делали ты можешь увидеть при запуске программы)
    """

    def change_text(self):
        self.App.Ui.Buttons.change_value("first_button", "text", "ура!")
        self.App.update()
        
    def game_menu(self):
        self.App.Ui.clear()

        self.App.Ui.Buttons.new("first_button", "circle", 25, (0, 0), self.change_text, "orange", 
                        5, "red", "Нажми!", ("Arial", 10, "normal"), "black")

        self.App.update()

hotkeys = {} 
hotkeys_release = {} #важные переменные которые лучше не трогать
listener = None

def run():
    global listener
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    Game = App()
    listener = keyboard.Listener(on_press=Game.on_press, on_release=Game.on_release)
    listener.start() 
    Game.Scenes.game_menu() #! важная строка game_menu - название функции которая выполниться с самого запуска игры 
    Game.update()           # название может быть любым. Не забудь добавить кнопки ля перехода на другие сцены
    Game.Screen.mainloop()

if __name__ == "__main__":
    try:
        run()
    except Exception as e:  #это система сохранения ошибок в лог
        print(e)
        print("Произошла ошибка! Лог ошибки последней игры находиться в файле exception_log.txt")
        with open("assets/exception_log.txt", "r", encoding="utf-8") as file:
            last = file.read()
            file.write(last + f"[ERROR] TIME {datetime.datetime.now()}: {e}" + "\n")
            listener.join()

listener.join()