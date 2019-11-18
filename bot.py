# bot.py
import os
import random
import sqlite3
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# 2
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")

@bot.command(name = "addMission", help = "Adds a new mission with given name. Use quotations for multi-word names")
async def addMission(ctx, mission: str):
    """
    Adds a new entry inside the missions table.
    Adds a new table named mission_id.
    Returning the mission_id with answering the client command.
    """
    conn = sqlite3.connect("slotlist.db")
    cursor = conn.cursor()

    # Adding the new entry inside the missions table with given name and highest + 1 mission_id
    mission_id = highest_mission_id() + 1
    sql = "INSERT INTO missions (mission_id, mission_name) VALUES (?, ?)"
    cursor.execute(sql, [(mission_id), (mission)])

    # Sending a message to the client
    send_message = "{} Your mission ID for >{}< is: {}".format(ctx.author.mention, mission, mission_id)
    await ctx.send(send_message)

    # Creating a new table named with the unique mission_id
    sql = 'CREATE TABLE "{}" (id INTEGER NOT NULL PRIMARY KEY)'.format(mission_id)
    cursor.execute(sql)

    conn.commit()
    conn.close()

    return

def highest_mission_id():
    """
    Returning the highest mission_id.
    """
    conn = sqlite3.connect("slotlist.db")
    cursor = conn.cursor()

    sql = "SELECT MAX(mission_id) FROM missions"
    cursor.execute(sql)
    data = cursor.fetchall()
    highest_mission_id = data[0][0]

    if highest_mission_id == None:
        highest_mission_id = 0

    conn.commit()
    conn.close()

    return highest_mission_id

@bot.command(name = "addSlots", help = "Adding the slots for the given mission based on a slots.txt inside the bot folder")
async def addSlots(ctx, mission: int):
    """
    Adding a new numerated column with linevalue for each line inside the slots.txt.
    Returning the added slots with answering the client command.
    """
    file = open(os.getcwd() + "/slots.txt", "r")
    fileLines = file.readlines()

    conn = sqlite3.connect("slotlist.db")
    cursor = conn.cursor()
    slot_id = 1

    sql = 'INSERT INTO "{}" (id) VALUES ({})'.format(mission, len(fileLines))
    cursor.execute(sql)

    for x in fileLines:
        sql = 'ALTER TABLE "{}" ADD COLUMN s{}n text'.format(mission, slot_id)
        cursor.execute(sql)
        sql = 'UPDATE "{}" SET s{}n = "{}"'.format(mission, slot_id, x[0:-1])
        cursor.execute(sql)
        sql = 'ALTER TABLE "{}" ADD COLUMN s{} text'.format(mission, slot_id)
        cursor.execute(sql)
        slot_id = slot_id + 1

    send_message = "{} You successfully added {} slots for >{}<".format(ctx.author.mention, len(fileLines), mission_convert(mission))
    await ctx.send(send_message)

    conn.commit()
    conn.close()

def mission_convert(mission_id):
    """
    Returning the mission_name for a mission_id.
    """
    conn = sqlite3.connect("slotlist.db")
    cursor = conn.cursor()

    sql = "SELECT mission_name FROM missions WHERE mission_id=?"
    cursor.execute(sql,[(mission_id)])
    data = cursor.fetchall()
    mission_name = data[0][0]

    if mission_name == None:
        mission_name = "Not found"

    conn.commit()
    conn.close()

    return mission_name

@bot.command(name = "missions", help = "List all available missions")
async def missions(ctx):
    """
    Will list all available missions.
    Returning with answering the client command.
    """
    conn = sqlite3.connect("slotlist.db")
    cursor = conn.cursor()

    sql = "SELECT * FROM missions"
    cursor.execute(sql)
    data = cursor.fetchall()

    send_message = ""
    for x in range(0, len(data)):
        send_message = send_message + "{}: {}\n".format(data[x][0], data[x][1])

    await ctx.send(send_message)


    conn.commit()
    conn.close()

@bot.command(name = "missioninfo", help = "List all available mission related informations")
async def missioninfo(ctx, mission: int):
    """
    Will list all available mission related informations.
    Returning with answering the client command.
    """
    conn = sqlite3.connect("slotlist.db")
    cursor = conn.cursor()

    sql = 'SELECT id FROM "{}"'.format(mission)
    cursor.execute(sql)
    data = cursor.fetchall()
    nslots = data[0][0]

    sql = 'SELECT * FROM "{}"'.format(mission)
    cursor.execute(sql)
    data = cursor.fetchall()

    send_message = "{}: {}\n".format(mission, mission_convert(mission))

    group = ""
    j = 1
    for i in range(1, nslots + 1):
        group_name = data[0][j].split(",")[0]
        if group != group_name:
            send_message = send_message + "\n**{}**:\n".format(group_name)
            group = group_name
        send_message = send_message + "{}: {}{}\n".format(i, data[0][j].split(",")[1], get_name(data, j + 1))
        j = j + 2
    await ctx.send(send_message)


    conn.commit()
    conn.close()

def get_name(data, i):
    r = data[0][i]
    if r == None:
        return ""
    else:
        return (" - " + r[0:-5])

@bot.command(name = "slot", help = "Slot yourself for a mission")
async def slot(ctx, mission: int, slot: int):
    """
    Connects to the database and checks for already assigned players.
    If not it will assign the player to the slot.
    """
    conn = sqlite3.connect("slotlist.db")
    cursor = conn.cursor()

    if already_slotted(ctx.author, mission):
        conn.commit()
        conn.close()
        send_message = "{} You are already slotted".format(ctx.author.mention)
        await ctx.send(send_message)
        return

    sql = 'SELECT s{} FROM "{}"'.format(slot, mission)
    cursor.execute(sql)
    data = cursor.fetchall()
    slotdb = data[0][0]

    if slotdb == None:
        sql = 'UPDATE "{}" SET s{} = "{}"'.format(mission, slot, ctx.author, slot)
        cursor.execute(sql)

        send_message = "{} You have been slotted for #{} at >{}<".format(ctx.author.mention, slot, mission_convert(mission))
        await ctx.send(send_message)
    else:
        send_message = "{} Slot is already taken. I'm sorry".format(ctx.author.mention)
        await ctx.send(send_message)

    conn.commit()
    conn.close()

def already_slotted(name, mission):
    """
    Connects to the database and checks all slots for already slotted player.
    If found it will return true
    """
    conn = sqlite3.connect("slotlist.db")
    cursor = conn.cursor()
    sql = 'SELECT * FROM "{}"'.format(mission)
    cursor.execute(sql)
    data = cursor.fetchall()
    conn.commit()
    conn.close()
    for x in range(1, data[0][0] + 1):
        if data[0][x * 2] == str(name):
            return True
    return False

bot.run(token)