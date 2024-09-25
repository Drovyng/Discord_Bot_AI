import json
import os.path
import time

import token

AI_HISTORY = {}
AI_PROMT = {}

BOT_TOKEN = token.BOT_TOKEN
AUTHOR_IDS = [781904298900455435, 1091266454080471111, 912996021041238056]
CHANNEL_ID = 1288176450167509074
THREAD_IDS = []
PAINT_THREAD = 1288565016647438398
SAVE_TIME = time.perf_counter()


def save1():
    if SAVE_TIME + 30 < time.perf_counter():
        save()


def save():
    global SAVE_TIME
    SAVE_TIME = time.perf_counter()
    with open("config.json", "w", encoding="UTF-8") as file:
        json.dump({"AI_PROMT" : AI_PROMT, "THREAD_IDS" : THREAD_IDS, "AI_HISTORY": AI_HISTORY}, file)


def reload():
    global AI_PROMT, THREAD_IDS, AI_HISTORY
    if not os.path.exists("config.json"):
        save()
        return

    with open("config.json", "r", encoding="UTF-8") as file:
        loaded = json.load(file)
        AI_PROMT = loaded["AI_PROMT"]
        THREAD_IDS = loaded["THREAD_IDS"]
        AI_HISTORY = loaded["AI_HISTORY"]

reload()
