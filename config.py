import json
import os.path
import time

import tokenFile

AI_HISTORY = {}
AI_PROMT = {}

BOT_TOKEN = tokenFile.BOT_TOKEN
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
        json.dump({"AI_PROMT" : AI_PROMT, "THREAD_IDS" : THREAD_IDS, "AI_HISTORY": AI_HISTORY}, file, ensure_ascii=False)


def parse_dict_int_any(to_parse: dict) -> dict:
    result = {}
    for k in to_parse:
        result[int(k)] = to_parse[k]
    return result


def reload():
    global AI_PROMT, THREAD_IDS, AI_HISTORY
    if not os.path.exists("config.json"):
        save()
        return

    with open("config.json", "r", encoding="UTF-8") as file:
        loaded = json.load(file)
        THREAD_IDS = loaded["THREAD_IDS"]
        AI_PROMT = parse_dict_int_any(loaded["AI_PROMT"])
        AI_HISTORY = parse_dict_int_any(loaded["AI_HISTORY"])

reload()

BOT_INSTRUCTIONS = ["""
> # Инструкция по пользованию
> - __ИИ отвечает на сообщения только в специальных ветках!__
> 
> ## Чат с ИИ:
> 
> - Что бы написать сообщение и ИИ не отвечал на него поставьте в самом начале сообщения любой из __этих__ символов: ```> ? . , % $ -```
> 
> - Вы __можете__ задать ИИ промт (личность/инструкцию) командой `!Промт: [ваш промт]` и вы сможете с ним "поиграть". Например в угадай число или же во что угодно! Это же ИИ!
> - Вы __можете__ очистить чат (и историю ИИ) командой `!Очистить`.
> __Регистр команд **не важен**__
> 
> ## Рисование ИИ:
> 
> - Для того чтобы ИИ Сгенерировал вам картинку напишите в  следующее: `Нарисуй: [Ваш запрос]`
> **Важно!** Если с момента генерации последней картинки не прошло 30 секунд то бот __отклонит__ запрос и поставит на ваше сообщение 3 реакции: ⌛ ❌ ⏳ 
> 
> ## Что может НЕ сделает ИИ:
> 
> - Может не ответить на слишком плохие или написаные неправильно слова.
> 
> - Не сгенерировать картинку если в запросе присутствует ненормативная лексика или слово написано не верно.
"""[1:-1], """
> # Список чатов:
> 
> ## Рисовалка:
> - <#1288565016647438398>
> ## Общение:
> - <#1288592450746716201>
> - <#1288592009237364846>
> - <#1288592011351556108>
> - <#1288592012609847348>
> - <#1288592014463598632>
> - <#1288592016321806428>
> - <#1288592018230087810>
> - <#1288592019639500883>
> - <#1288592020809715847>
> - <#1288592023083028562>
"""[1:-1]]