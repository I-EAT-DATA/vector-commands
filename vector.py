import anki_vector
import random
import time
import argparse
from datetime import datetime
from datetime import date
from PIL import Image
from anki_vector.events import Events
from anki_vector.util import degrees
from anki_vector import user_intent
from anki_vector import audio
import requests
import json

def phrase_anim(text, delay, anim):
    global robot
    print(type(robot))
    robot.behavior.say_text(text)
    time.sleep(delay)
    robot.anim.play_animation_trigger(anim)

def turn_to_face():
    global robot

    robot.behavior.drive_off_charger()

    robot.behavior.set_head_angle(degrees(45.0))
    robot.behavior.set_lift_height(0.0)

    visable_face = None

    while not visable_face:
        for face in robot.world.visible_faces:
            print(face)
            visable_face = face

    robot.behavior.turn_towards_face(visable_face)

def hello():
    global robot
    now = datetime.now()

    hellos = ["hello there", "hi", "nice to see you", "hello", "howdy partner", "i'm grumpy", "leave me alone", "hi there"]
    animations = ["ReactToGreeting", "DriveEndHappy", "PRDemoGreeting", "GreetAfterLongTime"]

    chance = random.randint(1, 3)

    if chance == 1:
        phrase_anim(random.choice(hellos), random.randrange(1, 3), random.choice(animations))
    else:
        if now.hour > 0 and now.hour < 8:
            phrase_anim("Good Morning!", 1, "ReactToGoodMorning")

        if now.hour < 24 and now.hour > 16:
            phrase_anim("Good Evening!", 1, "ReactToGoodNight")

def fistbump():
    global robot

    turn_to_face()

    robot.anim.play_animation_trigger("FistBumpRequestOnce")

    time.sleep(3)

    robot.anim.play_animation_trigger("FistBumpSuccess")

def photo():
    global robot

    turn_to_face()

    captured_img = robot.camera.capture_single_image()

    captured_img.raw_image.save(datetime.today().strftime(r"%m.%d.%Y_%I.%M.%S.png"))

    robot.anim.play_animation("anim_photo_shutter_01")

def explore():
    global robot

    robot.behavior.drive_off_charger()
    robot.behavior.look_around_in_place()

def get_age():
    global robot

    registered = date(2019, 7, 31)
    age = (date.today() - registered).days

    print(age)

    robot.behavior.say_text("I am {} days old".format(age))

    robot.anim.play_animation_trigger("GreetAfterLongTime")

def get_weather():
    global robot

    city = "North Oaks"

    response = requests.get("http://api.openweathermap.org/data/2.5/weather?appid=WEATHERKEYHERE&q=" + city).json()

    print(response)

    weather_response = response["main"]

    current_temperature_f = round((weather_response["temp"] - 273.15) * 9/5 + 32)

    robot.behavior.say_text("In {} it is currently {} degrees fahrenheit with {}".format(city, current_temperature_f, response["weather"][0]["description"]))

    if response["weather"][0]["main"] == "Clouds":
        robot.anim.play_animation("anim_weather_cloud_01")
    if response["weather"][0]["main"] == "Rain":
        robot.anim.play_animation("anim_weather_rain_01")
    if response["weather"][0]["main"] == "Thunderstorm":
        robot.anim.play_animation("anim_weather_thunderstorm_01")
    if response["weather"][0]["main"] == "Clear":
        if datetime.fromtimestamp(response["sys"]["sunrise"]).hour < datetime.now().hour and datetime.fromtimestamp(response["sys"]["sunset"]).hour > datetime.now().hour:
            robot.anim.play_animation("anim_weather_stars_01")
        else:
            robot.anim.play_animation("anim_weather_sunny_01")
    
parser = argparse.ArgumentParser(description = 'Vector voice commands')

funcs = {
        'hello': hello,
        'fistbump': fistbump,
        'photo': photo,
        'explore': explore,
        'age': get_age,
        'go forward': lambda: robot.anim.play_animation_trigger("MovementDriveForward"),
        'go backwards': lambda: robot.anim.play_animation_trigger("MovementDriveBackward"),
        'turn left': lambda: robot.anim.play_animation_trigger("MovementTurnLeft"),
        'turn right': lambda: robot.anim.play_animation_trigger("MovementTurnRight"),
        'turn around': lambda: robot.anim.play_animation_trigger("MovementTurnAround"),
        'go home': lambda: robot.behavior.drive_on_charger(),
        'volume low': lambda: robot.audio.set_master_volume(audio.RobotVolumeLevel.LOW),
        'volume medium': lambda: robot.audio.set_master_volume(audio.RobotVolumeLevel.MEDIUM),
        'volume high': lambda: robot.audio.set_master_volume(audio.RobotVolumeLevel.HIGH),
        'what is the date': lambda: robot.behavior.say_text("The date is {}".format(date.today())),
        'what day is it': lambda: robot.behavior.say_text("Today is {}".format(date.today().strftime('%A'))),
        'what time is it': lambda: robot.behavior.say_text("The time is {}".format(datetime.now().strftime('%I:%M %p'))),
        'look at me': lambda: turn_to_face(),
        'good robot': lambda: robot.anim.play_animation_trigger("Feedback_GoodRobot"),
        'bad robot': lambda: robot.anim.play_animation_trigger("Feedback_BadRobot"),
        'sorry': lambda: robot.anim.play_animation_trigger("Feedback_Apology"),
        'i hate you': lambda: robot.anim.play_animation_trigger("Feedback_MeanWords"),
        'i love you': lambda: robot.anim.play_animation_trigger("Feedback_ILoveYou"),
        'happy new year': lambda: robot.anim.play_animation_trigger("SeasonalHappyNewYear"),
        'happy holidays': lambda: robot.anim.play_animation_trigger("SeasonalHappyHolidays"),
        'what is the weather': get_weather,
        }

parser.add_argument('command', choices = funcs.keys(), help = "Enter the name of a listed function after vector.py")
args = parser.parse_args()

func = funcs[args.command]

with anki_vector.Robot(enable_face_detection = True) as robot:
    func()

