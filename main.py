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
        self.maxsize = (get_monitors()[0].width, get_monitors()[0].height)
        self.selected_machine = "LaGG3"
        self.selected_map = ""
        self.player = None
        self.run_game = False
        self.Screen = turtle.Screen()
        self.Screen.listen()
        self.Screen.getcanvas().focus_force()
        root = self.Screen._root
        root.iconbitmap("i.ico")
        self.Ui = Ui(self)
        self.Scenes = Scenes(self)
        self.Machines = Machines(self)
        self.Maps = Maps(self)
        self.Screen.screensize(self.maxsize[0], self.maxsize[1])
        self.Screen.setup(self.maxsize[0] / 2, self.maxsize[1] / 1.5)
        self.Screen.bgcolor("black")
        self.Screen.tracer(0)
        self.Screen.delay(0)
        self.Screen.title("War Turtle")  
        self.Screen.onscreenclick(self.click, 1)
        hotkeys["esc"] = self.Scenes.exit_window
        self.renderer = turtle.Turtle()  
        self.renderer.penup()
        self.renderer.hideturtle()
        self.renderer.speed(0)
        self.bullet_drawer = None
        self.game_settings = {}
        self.settings = {}
        self.bullets = []
        self.fps = 30
        self.language = "an"
        self.slow = 100
        self.shapes = []
        self.version = "i_hope_is_not_last" 

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

    def rotate_texture(self, path, angle, name):
        first = Image.open(path)
        first = first.resize((52, 52), Image.Resampling.LANCZOS)                 
        rotated = first.rotate(angle, expand=True, fillcolor=(0, 0, 0, 0)) 
        photo = ImageTk.PhotoImage(rotated.convert("RGBA")) 
        self.Screen.addshape(f"{name}_{angle}", turtle.Shape("image", photo))

    def begin_game(self):
        if self.selected_map != "":
            self.bullet_drawer = turtle.Turtle()
            self.bullet_drawer.hideturtle()
            self.bullet_drawer.penup()
            self.bullet_drawer.color(253,207,88)
            self.bullet_drawer.speed(0)
            self.Maps.load_map()
            cls = self.Machines.get(self.selected_machine).cls
            if cls == "Plane":
                player = PlayerPlane(self, self.selected_machine)
            else:
                player = PlayerTank(self, self.selected_machine)
            player.goto(-self.Maps.registry[self.selected_map].size[0] // 2, 0)
            self.run_game = True
            while self.run_game:
                player.move()
                self.move_bullet()
                self.draw_bullet()
                time.sleep(1 / self.fps)
                self.update()
        else:
            self.Scenes.map_not_selected()

    def new_bullet(self, armor_projectile, speed, size, start_pos, angle, mass):
        self.bullets.append({
            "armor_projectile": armor_projectile,
            "size": size,
            "speed": speed,
            "angle": angle,
            "pos": start_pos,
            "mass": mass
        })

    def draw_bullet(self):
        for blt in self.bullets:
            self.bullet_drawer.goto(blt["pos"])
            x_pos = blt["pos"][0]
            y_pos = blt["pos"][1]
            half_a = blt["size"][0] / 2
            half_b = blt["size"][0] / 2
            cos = math.cos(math.radians(blt["angle"]))
            sin = math.sin(math.radians(blt["angle"]))
            self.bullet_drawer.pendown()
            self.bullet_drawer.begin_fill()
            self.bullet_drawer.goto(x_pos + (-half_a * cos + half_b * sin), y_pos + (-half_a * sin - half_b * cos))
            self.bullet_drawer.goto(x_pos + (half_a * cos + half_b * sin), y_pos + (half_a * sin - half_b * cos))
            self.bullet_drawer.goto(x_pos + (half_a * cos + -half_b * sin), y_pos + (half_a * sin + half_b * cos))
            self.bullet_drawer.goto(x_pos + (-half_a * cos + -half_b * sin), y_pos + (-half_a * sin + half_b * cos))
            self.bullet_drawer.end_fill()
            self.bullet_drawer.penup()

    def move_bullet(self):
        for blt in self.bullets:
            blt["pos"][0] = blt["pos"][0] + blt["speed"] * math.sin(math.radians(blt["angle"])) / self.slow
            blt["pos"][1] = blt["pos"][1] + blt["speed"] * math.cos(math.radians(blt["angle"])) / self.slow
            blt["speed"] = blt["speed"] - 1 - blt["mass"]

    def check_colision(self):
        pass

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

    def random_player_name(self):
        name = "player"
        for _ in range(5):
            name = name + str(random.randint(0, 9))
        with open("player_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        data["player_name"] = name
        with open("player_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def close(self):
        self.Screen.bye()
        exit()

class Ui:
    def __init__(self, App):
        self.Buttons = Buttons(self)
        self.Labels = Labels(self)
        self.Frames = Frames(self)
        self.CheckBox = CheckBox(self)
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

class PlayerPlane:
    def __init__(self, App, machine):
        self.App = App
        self.data = self.App.Machines.get(machine)
        self.health = self.data.health
        self.angle = 270
        self.y = 0
        self.forward = False
        self.back = False
        self.x = 0
        self.angle_speed = 0
        self.boost = 0 
        self.speed = 0
        self.weapon = {
            "capacity": self.data.weapons[0]["capacity"],
            "less_shells": self.data.weapons[0]["capacity"],
            "shell_for_second": self.data.weapons[0]["shell_for_second"],
            "time_to_shoot": 0,
            "armor_projectile": self.data.weapons[0]["armor_projectile"],
            "offset": self.data.weapons[0]["offset"],
            "shell_mass": self.data.weapons[0]["bullet_mass"]
        }
        self.extra_weapon = None if len(self.data.weapons) == 1 else {
            "capacity": self.data.weapons[1]["capacity"],
            "less_shells": self.data.weapons[1]["capacity"],
            "shell_for_second": self.data.weapons[1]["shell_for_second"],
            "time_to_shoot": 0,
            "armor_projectile": self.data.weapons[1]["armor_projectile"],
            "offset": self.data.weapons[1]["offset"],
            "shell_mass": self.data.weapons[0]["bullet_mass"]
        }
        self.name = self.data.name
        self.rotate_for_second = self.data.rotate_for_second
        self.speed_for_second = self.data.speed_for_second
        self.max_speed = self.data.max_speed
        self.cls = self.data.cls
        self.image_path = self.data.shape
        self.img = turtle.Turtle()
        self.img.penup()
        self.img.speed(0)
        self.speed = 300
        self.link_keys()

    def shoot(self):
        pass

    def goto(self, x, y):
        self.img.goto(x, y)
        self.x = x
        self.y = y

    def link_keys(self):
        hotkeys["w"] = self.up_speed
        hotkeys_release["w"] = self.stop
        hotkeys["s"] = self.slow_down
        hotkeys_release["s"] = self.stop
        hotkeys["a"] = self.right
        hotkeys_release["a"] = self.stop_rotate
        hotkeys["d"] = self.left
        hotkeys_release["d"] = self.stop_rotate
        self.App.Screen.onscreenclick(self.shoot, 1)

    def up_speed(self):
        self.forward = True

    def do_up_speed(self):
        if self.speed >= self.max_speed:
            self.boost = 0
            return
        self.boost += self.speed_for_second

    def air_resistance(self):
        if self.boost > 0:
            self.boost -= self.speed_for_second / 1.5
        else:
            if self.speed > 300:
                self.speed -= self.speed_for_second / 1.5

    def do_slow_down(self):
        if self.speed > 300:
            if self.boost <= 0:
                self.speed -= self.speed_for_second 
            else:
                self.boost -= self.speed_for_second
        else:
            self.speed = 300
            self.boost = 0

    def slow_down(self):
        self.back = True

    def stop(self):
        self.forward = False
        self.back = False

    def right(self):
        self.angle_speed = self.rotate_for_second / self.App.fps

    def left(self):
        self.angle_speed = -self.rotate_for_second / self.App.fps

    def stop_rotate(self):
        self.angle_speed = 0

    def move(self):
        self.speed += self.boost / self.App.slow
        self.angle += self.angle_speed
        if self.forward:
            self.do_up_speed()
        if self.back:
            self.do_slow_down()
        self.air_resistance()
        self.x -= self.speed / self.App.slow * math.sin(math.radians(self.angle))
        self.y += self.speed / self.App.slow * math.cos(math.radians(self.angle))
        self.img.goto(self.x, self.y)
        if not self.name + "_" + str(round(self.angle)) in self.App.shapes:
            self.App.rotate_texture(self.image_path, round(self.angle), self.name)
            self.App.shapes.append(self.name + "_" + str(round(self.angle)))
        self.img.shape(self.name + "_" + str(round(self.angle)))

    """def unlink_keys(self):
        self.App.Screen.onkeypress(None, "w")
        self.App.Screen.onkeyrelease(None, "w")
        self.App.Screen.onkeypress(None, "s")
        self.App.Screen.onkeyrelease(None, "s")
        self.App.Screen.onkeypress(None, "d")
        self.App.Screen.onkeyrelease(None, "d")
        self.App.Screen.onkeypress(None, "a")
        self.App.Screen.onkeyrelease(None, "a")"""

class PlayerTank:
    def __init__(self, App, machine_obj):
        self.App = App
        self.data = self.App.Machines.get(machine_obj)
        self.health = self.data.health
        self.angle = 270
        self.y = 0
        self.forward = False
        self.back = False
        self.x = 0
        self.angle_speed = 0
        self.boost = 0 
        self.speed = 0
        self.name = self.data.name
        self.rotate_for_second = self.data.rotate_for_second
        self.speed_for_second = self.data.speed_for_second
        self.max_speed = self.data.max_speed
        self.cls = self.data.cls
        self.targer_tower = 270
        self.angle_tower = 270
        self.tower_rotate_speed = 0
        self.max_back_speed = self.data.max_back_speed
        self.image_path = self.data.null_shape
        self.image_path_tower = self.data.tower_shape
        self.weapon = {
            "capacity": self.data.weapons[0]["capacity"],
            "shell_for_second": self.data.weapons[0]["shell_for_second"],
            "time_to_shoot": 0,
            "armor_projectile": self.data.weapons[0]["armor_projectile"],
            "offset": self.data.weapons[0]["offset"]
        }
        self.extra_weapon = None if len(self.data.weapons) == 1 else {
            "capacity": self.data.weapons[1]["capacity"],
            "shell_for_second": self.data.weapons[1]["shell_for_second"],
            "time_to_shoot": 0,
            "armor_projectile": self.data.weapons[1]["armor_projectile"],
            "offset": self.data.weapons[1]["offset"]
        }
        self.img = turtle.Turtle()
        self.img.penup()
        self.img.speed(0)
        self.img_tower = turtle.Turtle()
        self.img_tower.penup()
        self.img_tower.speed(0)
        self.tower_rotate_speed = self.data.tower_rotate_speed
        self.x_tower_ofs = self.data.tower_x_offset
        self.y_tower_ofs = self.data.tower_y_offset
        self.link_keys()

    def shoot(self):
        pass

    def goto(self, x, y):
        self.img_tower.goto(x + self.x_tower_ofs, y + self.y_tower_ofs)
        self.img.goto(x, y)
        self.x = x
        self.y = y

    def link_keys(self):
        hotkeys["w"] = self.up_speed
        hotkeys_release["w"] = self.stop
        hotkeys["s"] = self.slow_down
        hotkeys_release["s"] = self.stop
        hotkeys["a"] = self.right
        hotkeys_release["a"] = self.stop_rotate
        hotkeys["d"] = self.left
        hotkeys_release["d"] = self.stop_rotate
        self.App.Screen.onscreenclick(self.shoot, 1)
        canvas = self.App.Screen.getcanvas()
        canvas.bind("<Motion>", self.get_tower_targer)

    def up_speed(self):
        self.forward = True

    def do_up_speed(self):
        if self.speed >= self.max_speed:
            self.boost = 0
            return
        self.boost += self.speed_for_second

    def air_resistance(self):
        if self.boost > 0:
            self.boost -= self.speed_for_second / 1.5
        elif self.boost < 0:
            self.boost += self.speed_for_second / 1.5
        else:
            if self.speed > 0:
                self.speed -= self.speed_for_second / 1.5
            elif self.speed < 0:
                self.speed += self.speed_for_second / 1.5

    def get_tower_targer(self, event):
        turtle_x = event.x - self.App.Maps.registry[self.App.selected_map].size[0] / 2
        turtle_y = self.App.Maps.registry[self.App.selected_map].size[1] / 2 / 2 - event.y 
        dy = turtle_y - self.y + self.data.tower_y_offset
        dx = turtle_x - self.x + self.data.tower_x_offset
        self.targer_tower = math.degrees(math.atan2(dy, dx))

    def move_tower(self):
        diff = self.targer_tower - self.angle_tower
        delta = (diff + 180) % 360 - 180
        if abs(delta) <= self.tower_rotate_speed / self.App.fps:
            self.angle_tower = self.targer_tower
            return
        if delta > self.tower_rotate_speed / self.App.fps:
            self.angle_tower += self.tower_rotate_speed / self.App.fps
        else: 
            self.angle_tower -= self.tower_rotate_speed / self.App.fps
   
    def do_slow_down(self):
        if self.speed <= self.max_back_speed:
            self.boost = 0
            return
        self.boost -= self.speed_for_second 

    def slow_down(self):
        self.back = True

    def stop(self):
        self.forward = False
        self.back = False

    def right(self):
        self.angle_speed = self.rotate_for_second / self.App.fps

    def left(self):
        self.angle_speed = -self.rotate_for_second / self.App.fps

    def stop_rotate(self):
        self.angle_speed = 0

    def move(self):
        self.speed += self.boost / self.App.slow
        self.angle += self.angle_speed
        if self.forward:
            self.do_up_speed()
        if self.back:
            self.do_slow_down()
        self.air_resistance()
        self.x -= self.speed / self.App.slow * math.sin(math.radians(self.angle))
        self.y += self.speed / self.App.slow * math.cos(math.radians(self.angle))
        self.img.goto(self.x, self.y)
        if not self.name + "_" + str(round(self.angle)) in self.App.shapes:
            self.App.rotate_texture(self.image_path, round(self.angle), self.name)
            self.App.shapes.append(self.name + "_" + str(round(self.angle)))
        self.img.shape(self.name + "_" + str(round(self.angle)))
        self.move_tower()
        rad = math.radians(self.angle)
        world_ofs_x = self.x_tower_ofs * math.cos(rad) - self.y_tower_ofs * math.sin(rad)
        world_ofs_y = self.x_tower_ofs * math.sin(rad) + self.y_tower_ofs * math.cos(rad)
        self.img_tower.goto(self.x + world_ofs_x, self.y + world_ofs_y)
        if not self.name + "_tower_" + str(round(self.angle + self.angle_tower)) in self.App.shapes:
            self.App.rotate_texture(self.image_path_tower, round(self.angle + self.angle_tower), self.name + "_tower")
            self.App.shapes.append(self.name + "_tower_" + str(round(self.angle + self.angle_tower)))
        self.img_tower.shape(self.name + "_tower_" + str(round(self.angle + self.angle_tower)))
        #print(f"{self.speed} км в ч")
        #print(f"{self.boost} ускорение")

    """def unlink_keys(self):
        self.App.Screen.onkeypress(None, "w")
        self.App.Screen.onkeyrelease(None, "w")
        self.App.Screen.onkeypress(None, "s")
        self.App.Screen.onkeyrelease(None, "s")
        self.App.Screen.onkeypress(None, "d")
        self.App.Screen.onkeyrelease(None, "d")
        self.App.Screen.onkeypress(None, "a")
        self.App.Screen.onkeyrelease(None, "a")"""
   
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

class CheckBox:
    def __init__(self, Ui):
        self.Ui = Ui
        self.check_boxes = []

class Bots:
    def __init__(self, App):
        self.App = App
        self.allies_bots = []
        self.enemy_bots = []

    def add(self, name, name_machine, team):
        pass

    def delete(self, name):
        pass

class Machines:
    def __init__(self, App):
        self.App = App
        self.Planes = Planes(self)
        self.Tanks = Tanks(self)
        self.Ships = Ships(self)
        self.player_machines = []

    def play(self, type, name):
        pass

    def get(self, name):
        try:
            machine = self.Planes.registry[name]
            return machine
        except:
            try:
                machine = self.Tanks.registry[name]
                return machine
            except:
                try:
                    machine = self.Ships.registry[name]
                    return machine
                except:
                    return self.Planes.registry[self.App.selected_machine]

class Planes:
    registry = {}

    def __init__(self, Machines):
        self.Machines = Machines
        self.Planes = ["LaGG3"]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Planes.registry[cls.__name__] = cls 

class LaGG3(Planes):
        name = "ЛаГГ-3"
        cls = "Plane"
        health = 100
        shape = "assets/images/lagg3.png"
        type = "Истребитель"
        max_speed = 549
        speed_for_second = 2 #набор скорости км/ч за секунду
        rotate_for_second = 35 #скорость поворота градусов в секунду
        thickness = 3        #средняя толщина брони
        colision = [["oval", 0, 0, 10, 30]] #форма колизии, смещение от центра по X, Y, размеры полуосей для овала, радиус для круга, стороны для прямоугольника
        weapons = [{
            "name": "Пулемёт БС",
            "capacity": 160,
            "shell_for_second": 13,
            "armor_projectile": 12, #пробиваемость мм
            "recharge": 10,
            "offset": [[0, 0]], # смещение по X, Y
            "bullet_mass": 0.2
        },
        {
            "name": "Пулемёт ШВАК",
            "capacity": 1200,
            "shell_for_second": 13,
            "armor_projectile": 8,
            "recharge": 5,
            "offset": [[0, 0], [0, 0]],
            "bullet_mass": 0.2
        }]
        
class Tanks:
    registry = {}

    def __init__(self, Machines):
        self.Machines = Machines
        self.tanks = ["T26"]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Tanks.registry[cls.__name__] = cls 

class T26(Tanks):
        name = "Т-26"
        cls = "Tank"
        health = 250
        shape = "assets/images/t26full.png"
        null_shape = "assets/images/t26null.png"
        tower_shape = "assets/images/t26tower.png"
        tower_rotate_speed = 46
        tower_x_offset = -1.6
        tower_y_offset = -0.1
        type = "Лёгкий танк"
        max_speed = 32
        max_back_speed = -3
        speed_for_second = 2       
        rotate_for_second = 35              
        thickness = 15          
        colision = [["rectangle", 0, 0, 25, 52]]
        weapons = [{
            "name": "пушка 20К",
            "capacity": 136,
            "shell_for_second": 0.2,
            "armor_projectile": 45,
            "recharge": 6,
            "offset": [[3, 3]],
            "bullet_mass": 1.3
        }]

class Ships:
    def __init__(self, Machines):
        self.Machines = Machines

class Scenes:

    def __init__(self, App):
        self.App = App
        self.image = turtle.Turtle()
        self.image.penup()
        self.image.speed(0)
        self.last_col = ""
        self.selected_map = ""
        self.map_images = []
        self.x = self.App.maxsize[0]
        self.y = self.App.maxsize[1]
        self.half_x = self.x / 2
        self.half_y = self.y / 2

    def select_map_window(self):
        self.App.Ui.hide_all()
        self.image.hideturtle()
        hotkeys["esc"] = self.stop_select
        self.App.Screen.onkeypress(self.stop_select, "Escape")
        self.last_col = self.App.Screen.bgcolor()
        self.App.Screen.bgcolor(35, 35, 35)
        height = 64
        otstup = 100
        for i, cls_name in enumerate(self.App.Maps.registry):
            cls = self.App.Maps.registry[cls_name]
            x = (i * height + otstup * i) - ((height + otstup) * len(self.App.Maps.registry)) // 4
            y = 0 + (i // 5) * height
            self.App.Ui.Buttons.new(f"map{cls.name}", "rectangle", [height, 25], (x, y - 10 * 8), self.select, "black", 2, "red", "выбрать", ("Arial", 12, "normal"), "red", action_arg = [cls.__name__, cls.name], group = "select_map")
            self.App.Ui.Labels.new(f"{cls.name}label", (x, y - 5 * 10), "center", cls.name, "white", ("Arial", 15, "normal"), group = "select_map")
            if not cls.name in self.App.shapes:
                map_img = Image.open(cls.mini_image)
                photo = ImageTk.PhotoImage(map_img)
                self.App.Screen.addshape(cls.name, turtle.Shape("image", photo))
                self.App.shapes.append(cls.name)
            t = turtle.Turtle()
            t.speed(0)
            t.penup()
            t.goto(x, y)
            t.shape(cls.name)
            self.map_images.append(t)
        self.App.Ui.Buttons.new(f"close_select_window", "rectangle", [40, 40], (self.half_x - 10 * 10, self.half_y - 10 * 10), self.stop_select, "black", 2, "red", "X", ("Arial", 20, "normal"), "red", group = "select_map")
        self.App.update()

    def close_map_not_selected(self, x=None, y=None):
        self.App.Ui.delete_group("map_not_selected")
        self.App.Screen.onscreenclick(self.App.click, 1)
        self.App.update()

    def map_not_selected(self):
        self.App.Ui.Frames.new("blackout_window", (28, 28, 28), [(-self.x / 8, self.y / 8), (self.x / 8, self.y / 8), 
                                (self.x / 8, -self.y / 8), (-self.x / 8, -self.y / 8)], group = "map_not_selected")
        self.App.Ui.Buttons.new(f"close_window", "rectangle", [30, 30], (self.x / 8 - 30, self.y / 8 - 30), self.close_map_not_selected, "black", 2, "red", "X", ("Arial", 20, "normal"), "red", group = "map_not_selected")
        self.App.Ui.Labels.new(f"map_not_select", (0, 0), "center", "Карта не выбрана", "white", ("Arial", 20, "normal"), group = "map_not_selected")
        self.App.Screen.onscreenclick(self.close_map_not_selected, 1)
        self.App.update()

    def select(self, name):
        self.App.selected_map = name[0]
        self.selected_map = name[1]
        self.stop_select()

    def stop_select(self):
        self.App.Screen.bgcolor(int(self.last_col[0]), int(self.last_col[1]), int(self.last_col[2]))
        for t in self.map_images:
            t.hideturtle()
            del t
        self.App.Ui.delete_group("select_map")
        self.App.Ui.show_all()
        self.App.Ui.Labels.change_value("selected_map", "text", f"выбранная карта:\n{self.selected_map}")
        self.App.Screen.onkeypress(self.exit_window, "Escape")
        hotkeys["esc"] = self.exit_window
        self.image.showturtle()
        self.App.update()

    def game_info(self):
        self.App.Ui.clear()
        self.App.Screen.bgcolor("black")
        self.App.Ui.Buttons.new("return", "rectangle", [110, 50], (0, -120), self.game_menu, "black", 3, "red", "обратно", ("Arial", 20, "normal"), "red")
        info = """
                            WAR TURTLE - это игра про сражения военной техники. 
 В этой игре вы сражаетесь с танками, самолетами, кораблями управляемыми ИИ.
       При развитии игры будет созданно больше различных техник, методов их 
                                    прокачки а так же онлайн сражения.
                                          Приятного времяпровождения!
        """
        self.App.Ui.Labels.new("info", (0, 50), "center", info, "red", ("Arial", 11, "normal"))
        self.App.update()
    
    def game_menu(self):
        self.App.Ui.clear()
        self.App.Screen.bgcolor("black")
        self.App.Ui.Labels.new("title", (0, 100), "center", "WAR TURTLE", "red", ("Arial", 25, "normal"))
        self.App.Ui.Buttons.new("start", "rectangle", [110, 50], (0, -50), self.play_menu, "black", 3, "red", "Играть", ("Arial", 20, "normal"), "red")
        self.App.Ui.Buttons.new("info", "rectangle", [110, 50], (0, -120), self.game_info, "black", 3, "red", "Информация", ("Arial", 13, "normal"), "red")
        self.App.update()

    def create_machines_buttons(self):
        height = self.y / 4 - self.y / 10
        lenght = (self.half_x - 10 - self.x / 4) * 2
        cells = math.floor(lenght / height)
        otstup = height * math.modf(lenght / height)[0] / cells + 1
        size = height - otstup
        for i in range(8):
            x = (-self.half_x + 10 + self.x / 4) + (size / 2 + otstup) + (size + otstup) * i
            y = -self.half_y + self.y / 4 - height / 2
            try:
                machine = self.App.Machines.player_machines[i] 
                self.App.Ui.Buttons.new(f"machine{i}", "rectangle", [size, size], (x, y), self.menu_load_machine, "black", 2, "red", machine, ("Arial", 13, "normal"), "red", action_arg = [machine])
            except:
                self.App.Ui.Buttons.new(f"more_machine", "rectangle", [size, size], (x, y), self.more_machine, "black", 2, "red", "+", ("Arial", 20, "bold"), "red")
                return
            
    def more_machine(self):
        pass

    def dont_exit(self):
        self.App.Ui.Buttons.delete("exit", "not_exit")
        self.App.Ui.Labels.delete("advice")
        self.App.Ui.Frames.delete("blackout")
        hotkeys["esc"] = self.exit_window
        self.App.Ui.show_all()
        self.App.update()

    def exit_window(self):
        self.App.Ui.hide_all()
        hotkeys["esc"] = self.dont_exit
        self.App.Ui.Frames.new("blackout", (35, 35, 35), [(-self.half_x, self.half_y), (self.half_x, self.half_y),
                                                           (self.half_x, -self.half_y), (-self.half_x, -self.half_y)])
        self.App.Ui.Labels.new("advice", (0, 50), "center", "Вы точно хотите выйти?", "white", ("Arial", 15, "normal"))
        self.App.Ui.Buttons.new("exit", "rectangle", [100, 50], (0, -40), self.App.close, "black", 3, "red", "Да", ("Arial", 25, "normal"), "red")
        self.App.Ui.Buttons.new("not_exit", "rectangle", [100, 50], (0, -110), self.dont_exit, "black", 3, "red", "Нет", ("Arial", 23, "normal"), "red")
        self.App.update()

    def play_menu(self):
        self.App.Ui.clear()
        self.App.Screen.bgcolor("blue")
        self.App.Screen.setup(self.x, self.y)
        self.App.Screen.screensize(self.x - 10, self.y - 10)
        self.App.Ui.Frames.new("machine_info", (42, 42, 42), [(-self.half_x + 10, self.half_y - 10 - self.y / 8), (-self.half_x + 10 + self.x / 6, self.half_y - 10 - self.y / 8), 
                                (-self.half_x + 10 + self.x / 6, -self.half_y + 10 + self.y / 4), (-self.half_x + 10, -self.half_y + 10 + self.y / 4)])
        self.App.Ui.Frames.new("gamemode_info", (42, 42, 42), [(self.half_x - 10, self.half_y - 10 - self.y / 8), (self.half_x - 10 - self.x / 6, self.half_y - 10 - self.y / 8), 
                                (self.half_x - 10 - self.x / 6, -self.half_y + 10 + self.y / 4), (self.half_x - 10, -self.half_y + 10 + self.y / 4)], group = "gamemode")
        self.App.Ui.Labels.new("offline", ((self.half_x * 2 - 10 * 2 - self.x / 6) / 2, self.half_y - 10 * 4 - self.y / 8), "center", "Офлайн", (76, 76, 76), ("Arial", 15, "normal"), "gamemode")
        self.App.Ui.Labels.new("mode", ((self.half_x * 2 - 10 * 2 - self.x / 6) / 2, self.half_y - 10 * 7 - self.y / 8), "center", "Режим:", "white", ("Arial", 17, "bold"), "gamemode")
        self.App.Ui.Labels.new("selected_map", ((self.half_x * 2 - 10 * 2 - self.x / 6) / 2, self.half_y - 10 * 14 - self.y / 8), "center", "выбранная карта: -", "white", ("Arial", 12, "bold"), "gamemode")
        self.App.Ui.Labels.new("modee", ((self.half_x * 2 - 10 * 2 - self.x / 6) / 2, self.half_y - 10 * 9 - self.y / 8), "center", "", "white", ("Arial", 13, "normal"), "gamemode")
        self.App.Ui.Buttons.new("select_map", "rectangle", [self.x / 6 - 10 * 6, 30], ((self.half_x * 2 - 10 * 2 - self.x / 6) / 2, self.half_y - 10 * 17 - self.y / 8), self.select_map_window, "black", 3, "black", "выбрать карту", ("Arial", 13, "bold"), "red", group = "gamemode")
        self.App.Ui.Frames.new("machine_buttons", (42, 42, 42), [(-self.half_x + 10 + self.x / 4, -self.half_y + self.y / 4), (self.half_x - 10 - self.x / 4, -self.half_y + self.y / 4), 
                                (self.half_x - 10 - self.x / 4, -self.half_y + self.y / 10), (-self.half_x + 10 + self.x / 4, -self.half_y + self.y / 10)])
        self.App.Ui.Buttons.new("play", "rectangle", [150, 80], (0, self.half_y - 80), self.App.begin_game, (42, 42, 42), 3, "red", "Играть", ("Arial", 25, "normal"), "red") 
        self.App.Ui.Buttons.new("info_hide_show", "rectangle", [16, 32], (-self.half_x + self.x / 6 + 30, self.y / 16), self.hide_info, (42, 42, 42), 3, "black", "<", ("Arial", 15, "bold"), "white")
        self.App.Ui.Buttons.new("gamemode_hide_show", "rectangle", [16, 32], (self.half_x - self.x / 6 - 30, self.y / 16), self.hide_gamemode, (42, 42, 42), 3, "black", ">", ("Arial", 15, "bold"), "white")
        self.menu_load_machine()
        self.create_machines_buttons()
        self.App.update()

    def add_bot_window(self, team):
        pass

    def show_bot_window(self, team):
        pass

    def hide_info(self):
        self.App.Ui.Frames.change_value("machine_info", "visible", False)
        self.App.Ui.Labels.change_value("machine_info", "visible", False)
        index = self.App.Ui.Buttons.get_index("info_hide_show")
        self.App.Ui.Buttons.buttons[index]["pos"] = (-self.half_x + 30, self.y / 16)
        self.App.Ui.Buttons.buttons[index]["text"] = ">"
        self.App.Ui.Buttons.buttons[index]["action"] = self.show_info  
        self.App.update()

    def show_info(self):
        self.App.Ui.Frames.change_value("machine_info", "visible", True)
        self.App.Ui.Labels.change_value("machine_info", "visible", True)
        index = self.App.Ui.Buttons.get_index("info_hide_show")
        self.App.Ui.Buttons.buttons[index]["pos"] = (-self.half_x + 30 + self.x / 6, self.y / 16)
        self.App.Ui.Buttons.buttons[index]["text"] = "<"
        self.App.Ui.Buttons.buttons[index]["action"] = self.hide_info  
        self.App.update()

    def hide_gamemode(self):
        self.App.Ui.hide_group("gamemode")
        index = self.App.Ui.Buttons.get_index("gamemode_hide_show")
        self.App.Ui.Buttons.buttons[index]["pos"] = (self.half_x - 30, self.y / 16)
        self.App.Ui.Buttons.buttons[index]["text"] = "<"
        self.App.Ui.Buttons.buttons[index]["action"] = self.show_gamemode 
        self.App.update()

    def show_gamemode(self):
        self.App.Ui.show_group("gamemode")
        index = self.App.Ui.Buttons.get_index("gamemode_hide_show")
        self.App.Ui.Buttons.buttons[index]["pos"] = (self.half_x - 30 - self.x / 6, self.y / 16)
        self.App.Ui.Buttons.buttons[index]["text"] = ">"
        self.App.Ui.Buttons.buttons[index]["action"] = self.hide_gamemode
        self.App.update()

    def menu_load_machine(self, machin = [""]):
        self.App.Ui.delete_group("bg")
        self.App.Ui.Labels.delete("machine_info")
        machine = self.App.Machines.get(machin[0])
        self.App.selected_machine = machine.__name__
        weapon_info = []
        for weapon in machine.weapons:
            if weapon["shell_for_second"] < 1:
                weapon_info.append("")
            else:
                weapon_info.append(weapon_info.append(", " + str(machine.weapons[0]["shell_for_second"]) + " в секунду"))
        info = f"""            ИНФОРМАЦИЯ

    Техника: {machine.name}
    Тип: {machine.type}
    Максимальная скорость: {machine.max_speed}
    Скорость поворота: 
    {machine.rotate_for_second}° в секунду
    Основное вооружение:
    {machine.weapons[0]["armor_projectile"]}мм {machine.weapons[0]["name"]}
    {machine.weapons[0]["capacity"]} снарядов{weapon_info[0]}
    перезарядка {machine.weapons[0]["recharge"]} сек
"""
        if len(machine.weapons) == 1:
            info +="""    Спомогательное вооружение: 
    не имеется
        """
        else:
            info +=f"""    Спомогательное вооружение:
    {machine.weapons[1]["armor_projectile"]}мм {machine.weapons[1]["name"]}
    {machine.weapons[1]["capacity"]} снарядов{weapon_info[1]}
    перезарядка {machine.weapons[1]["recharge"]} сек
    """
        offset = 0 if len(machine.weapons) == 2 else 30
        self.App.Ui.Labels.new("machine_info", (-self.half_x + self.x / 10 - 15, 0 + offset), "center", info, "white", ("Arial", 11, "normal"))
        match machine.cls:
            case "Tank":
                self.App.Screen.bgcolor(34, 139, 34)
                self.App.Ui.Labels.change_value("modee", "text", "танковый бой")
            case "Plane":
                self.App.Screen.bgcolor(68, 176, 255)
                self.App.Ui.Labels.change_value("modee", "text", "самолётный бой")
            case "Ship":
                self.App.Screen.bgcolor(0, 63, 255)
                self.App.Ui.Labels.change_value("modee", "text", "морской бой")
        if not machine.shape in self.App.shapes:
            machine_img = Image.open(machine.shape)
            photo = ImageTk.PhotoImage(machine_img)
            self.App.Screen.addshape(machine.shape, turtle.Shape("image", photo))
            self.App.shapes.append(machine.shape)
        self.image.shape(machine.shape)
        self.App.update()

class Maps:
    registry = {}

    def __init__(self, App):
        self.App = App
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Maps.registry[cls.__name__] = cls 

    def load_map(self):
        self.App.Ui.clear()
        self.App.Scenes.image.hideturtle()
        map = self.registry[self.App.selected_map]
        self.App.Screen.bgcolor(map.bgcolor)
        self.App.Screen.title(map.name)
        self.App.Screen.setup(width=map.size[0], height=map.size[1], startx=0, starty=0)
        self.App.Screen.screensize(map.size[0] - 10, map.size[1] - 10)

class EmptySky(Maps):
    name = "Чистое небо"
    size = (900, 900)
    for_machine = "plane"
    bgcolor = (68, 176, 255)
    mini_image = "assets/images/empty_sky.png"
    obstacle = {}

class SteppePath(Maps):
    name = "Степная тропинка"
    size = (900, 900)
    for_machine = "tank"
    bgcolor = "green"
    mini_image = "assets/images/steppe_path.png"
    obstacle = {}

version = "0.1 alpha"
hotkeys = {} 
hotkeys_release = {}
listener = None

def run():
    global listener
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    Game = App()
    with open("assets/player_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    if data["first_time"]:
        Game.random_player_name()
        data["first_time"] = False
        with open("assets/player_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    listener = keyboard.Listener(on_press=Game.on_press, on_release=Game.on_release)
    listener.start() 
    Game.Machines.player_machines = data["machines"]
    Game.settings = data["settings"]
    Game.language = data["language"]
    Game.version = version
    Game.Scenes.game_menu() 
    Game.update()
    Game.Screen.mainloop()

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print("Произошла ошибка! Лог ошибки последней игры находиться в файле exception_log.txt")
        with open("assets/exception_log.txt", "r", encoding="utf-8") as file:
            last = file.read()
            file.write(last + f"[ERROR] VERSION {version} TIME {datetime.datetime.now()}: {e}" + "\n")
            listener.join()

listener.join()