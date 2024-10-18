import traceback
from datetime import timedelta

import g4f, time
from discord import TextChannel, PermissionOverwrite, Thread, ChannelType, Poll
from g4f import Model
from g4f.Provider import *

model = Model(
    name          = "llama-3.1-8b",
    base_provider = "Meta",
    best_provider = IterListProvider([Blackbox])#, Airforce])
)
client = g4f.client.Client()

filter = ["а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я"] + list(""" !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ """)
async def get_response(messages: list[dict[str, str]], chat_id:int) -> str | None:
    try:
        if not chat_id in config.AI_PROMT:
            config.AI_PROMT[chat_id] = "Проси ввести команду \"`!промт [ваш промт]`\" для настройки!"
        msg: str = await g4f.ChatCompletion.create_async(
            model=g4f.models.llama_3_1_405b,
            messages=[
                         {"role": "system", "content": config.AI_PROMT[chat_id]+"\nEnter SHORT answers!\nEnter answers on RUSSIAN language!"},
                         {"role": "system", "content": "Current time is "+time.strftime("%a, %d %b %Y %H:%M")},
                     ] + messages[:]
        )
        msgL = msg.lower()
        cropCount = 0
        for i in range(0, min(10, len(msg))):
            if not msgL[-i] in filter:
                cropCount = cropCount + 1

        while cropCount > 0:
            cropCount = cropCount - 1
            msg = msg[:-1]
            msgL = msgL[:-1]
            if len(msgL) > 10 and not msgL[-10] in filter:
                cropCount = max(cropCount, 10)

        return msg
    except BaseException :
        traceback.print_exc()
        return None

from deep_translator import GoogleTranslator
translateEn = GoogleTranslator(source='auto', target='en')
translateRu = GoogleTranslator(source='auto', target='ru')


async def draw_image(promt) -> str:
    try:
        response = await client.images.async_generate(
            model="flux",
            #model='playground-v2.5',
            prompt=translateEn.translate(promt)
        )
        return response.data[0].url
    except BaseException as e:
        return f"[ОШИБКА ({e})]"


import discord, config
from discord.ext import commands
from discord.ext.commands.context import Message
bot = commands.Bot(help_command=None, command_prefix=">", intents=discord.Intents.all())


async def send_instruction():
    channel = bot.get_channel(config.CHANNEL_ID)
    await channel.purge(limit=100)
    for text in config.BOT_INSTRUCTIONS:
        await (await channel.send(content=text)).pin()
        await channel.purge(limit=1)


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="NexusPoins"))
    # poll = Poll("Когда начинаем новый сезон?",duration=timedelta(0, 0, 0, 0, 0, 8, 0))
    # poll.add_answer(text="След неделя (14.10.2024 - 20.10.2024)", emoji="👍")
    # poll.add_answer(text="ЗАВТРА!!!", emoji="✅")
    # poll.add_answer(text="Следущий месяц", emoji="❌")
    # await bot.get_channel(1265998299329200181).send(poll=poll)

    # await bot.get_channel(1295434904498212865).set_permissions(
    #     target=bot.get_guild(1257365949107933227).get_role(1257399413505261599),
    #     reason=None,
    #     read_message_history=True,
    #     send_messages=True,
    #     view_channel=True
    # )

    # async for thr in bot.get_channel(1264662345863528589).archived_threads():
    #     await thr.edit(archived=False, locked=False)
    #     await thr.edit(archived=True, locked=True, name="1СЗ | " + thr.name)

    print("Бот готов!")

last_time_image = -30

async def handle_message(msg: Message, hide=False):
    if hide:
        msg1 = msg
        msg = await msg.reply("[Аноним]: "+msg.content[1:])
        await msg1.delete()
    thread_id = msg.channel.id
    if not thread_id in config.AI_HISTORY:
        config.AI_HISTORY[thread_id] = []
    toAdd = {"role": "user", "content": translateRu.translate(msg.content)}


    response = await get_response(config.AI_HISTORY[thread_id][-10:]+[toAdd], thread_id)

    if not response is None and response != "":
        config.AI_HISTORY[thread_id].append(toAdd)
        config.AI_HISTORY[thread_id].append({"role": "assistant", "content": response})



        chunks = [response[i:i + 2000] for i in range(0, len(response), 2000)]

        previous_msg = msg

        for chunk in chunks:
            previous_msg = await previous_msg.reply(content=chunk.replace("*", "*\*"), mention_author=False)
    else:
        await msg.reply(content="[Произошла ошибка]", mention_author=False)

    config.AI_HISTORY[thread_id] = config.AI_HISTORY[thread_id][-20:]

    config.save1()


async def aexec(code):
    # Make an async function with the code and `exec` it
    exec(
        f'async def __ex(): ' +
        ''.join(f'\n {l}' for l in code.split('\n'))
    )
    # Get `__ex` from local variables, call it and return the result
    return await locals()['__ex']()

@bot.event
async def on_message(msg: Message):
    global last_time_image

    thread_id = msg.channel.id

    if msg.author.id in config.AUTHOR_IDS and msg.content.lower().startswith("питон-команда: "):
        await aexec(msg.content[15:])
        await msg.add_reaction("✅")
        return


    if msg.author.id == bot.user.id or not (thread_id in config.THREAD_IDS or thread_id == config.PAINT_THREAD):
        return

    if thread_id == config.PAINT_THREAD and len(msg.content) > 11 and msg.content.lower().startswith("нарисуй: "):
        if last_time_image + 25 < time.perf_counter():
            await (await msg.reply("Подождите...")).edit(content=f"Нарисовано: \"{msg.content[9:]}\"\n"+await draw_image(msg.content[9:]))
            last_time_image = time.perf_counter()
        else:
            await msg.add_reaction("⌛")
            await msg.add_reaction("❌")
            await msg.add_reaction("⏳")

        return



    if thread_id in config.THREAD_IDS:
        if msg.content.lower() == "!очистить":
            config.AI_HISTORY[thread_id] = []
            config.save1()
            await msg.channel.purge(limit=10000)
            await msg.channel.send(content=f"Текущий промт: ```{config.AI_PROMT[thread_id] if thread_id in config.AI_PROMT else " "}```\nВведите `!Промт: [ваш промт]` для изменения.")
        elif msg.content.lower().startswith("!промт: ") or msg.content.lower().startswith("!промт "):
            config.AI_PROMT[thread_id] = msg.content[7:]
            config.save1()
            await msg.add_reaction("✅")
        elif msg.content.lower().startswith("!удалить ") and len(msg.content) in [10, 11] and msg.content[9:] in [str(i) for i in range(1, 11)]:
            config.AI_HISTORY[thread_id] = config.AI_HISTORY[thread_id][:-int(msg.content[9:])]
            config.save()
            await msg.add_reaction("✅")
        elif msg.content.lower().startswith("!архивировать ") and len(msg.content) > 16 and msg.author.id in config.AUTHOR_IDS:
            thread: Thread = msg.channel
            await thread.edit(archived=True, locked=True, name="[АРХИВ] " + msg.content[14:])
            index = config.THREAD_IDS.index(thread_id)
            new_thread = await bot.get_channel(config.CHANNEL_ID).create_thread(
                 name=f"Чат {index+1}",
                 auto_archive_duration=10080,
                 slowmode_delay=5,
                 type=ChannelType.public_thread)
            config.THREAD_IDS[index] = new_thread.id
            config.save()
        else:
            if not msg.content[0] in [">", "?", ".", ",", "%", "$", "-", "!"]:
                async with msg.channel.typing():
                    await handle_message(msg, msg.content[0] == "&")
                    

bot.run(token=config.BOT_TOKEN)