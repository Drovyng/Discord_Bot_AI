import traceback

import g4f, time
from discord import TextChannel, PermissionOverwrite
from g4f import Model
from g4f.Provider import *

#from neiron import Free2GPTUpdated

model = Model(
    name          = "llama-3.1-8b",
    base_provider = "Meta",
    best_provider = IterListProvider([Airforce])
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
            # model="dall-e-3",
            # model="gemini",
            model='playground-v2.5',
            prompt=translateEn.translate(promt)
        )
        return response.data[0].url
    except BaseException:
        return "[ОШИБКА]"


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
    print("Бот готов!")

last_time_image = time.perf_counter()

async def handle_message(msg: Message):
    thread_id = msg.channel.id
    if not thread_id in config.AI_HISTORY:
        config.AI_HISTORY[thread_id] = []
    toAdd = {"role": "user", "content": translateRu.translate(msg.content)}

    response = await get_response(config.AI_HISTORY[thread_id]+[toAdd], thread_id)
    if not response is None:
        response = response.replace("*", "*\*")

    if not response is None and response != "":
        config.AI_HISTORY[thread_id].append(toAdd)
        config.AI_HISTORY[thread_id].append({"role": "assistant", "content": response})

        chunks = [response[i:i + 2000] for i in range(0, len(response), 2000)]

        previous_msg = msg

        for chunk in chunks:
            previous_msg = await previous_msg.reply(content=chunk, mention_author=False)
    else:
        await msg.reply(content="[Произошла ошибка]", mention_author=False)

    config.AI_HISTORY[thread_id] = config.AI_HISTORY[thread_id][-10:]

    config.save1()


@bot.event
async def on_message(msg: Message):
    global last_time_image

    thread_id = msg.channel.id
    
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
            config.save1()
            await msg.channel.purge(limit=10000)
        elif msg.content.lower().startswith("!промт: "):
            config.AI_PROMT[thread_id] = msg.content[8:]
            config.save1()
            await msg.delete()
        else:
            if not msg.content[0] in [">", "?", ".", ",", "%", "$", "-", "!"]:
                async with msg.channel.typing():
                    await handle_message(msg)
                    

bot.run(token=config.BOT_TOKEN)