import anki_vector
import random
import time
import argparse
from datetime import datetime

def phrase_anim(text, delay, anim):
    global robot
    print(type(robot))
    robot.behavior.say_text(text)
    time.sleep(delay)
    robot.anim.play_animation_trigger(anim)

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

parser = argparse.ArgumentParser(description = 'Vector voice commands')

funcs = {
        'hello' : hello
        }

parser.add_argument('command', choices = funcs.keys(), help = "Enter the name of a listed function after vector.py")
args = parser.parse_args()

func = funcs[args.command]

with anki_vector.Robot() as robot:
    func()
