# bot.py
import os, sqlite3, discord, sys, datetime
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import MemberConverter

# python 3 is needed to run this bot
if sys.version_info[0] == 2:
    print("Python 3 is required.")
    sys.exit(1)

# is a .env file inside the folder to leave the token for the bot outside the git
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# bot commands have prefix ! so all messages start with ! will trigger the bot commands
bot = commands.Bot(command_prefix='!')

# when the bot is initialized it will print a has connected to the terminal
@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")

@bot.command(name = "addMission", help = "Adds a new mission with given name. Use quotations for multi-word names")
async def addMission(ctx, mission: str, date: str, time: str):
    """
    Adds a new entry inside the missions table.
    Adds a new table named mission_id.
    Returning the mission_id with answering the client command.
    """
    # database connection
    conn = sqlite3.connect("slotlist.db")
    cursor = conn.cursor()

    # name must be compatible with discord channel name restrictions
    c = name_convert(mission)
    # if not tell the user how is the converted version
    if (mission != c):
        send_message = "{} Your mission will be renamed from >{}< to >{}<".format(ctx.author.mention, mission, c)
        await ctx.send(send_message)
        mission = c

    # Adding the new entry inside the missions table with given name and highest + 1 mission_id
    mission_id = highest_mission_id() + 1
    date = date + " " + time
    sql = "INSERT INTO missions (mission_id, mission_name) VALUES (?, ?)"
    cursor.execute(sql, [(mission_id), (mission)])

    # Sending a message to the client with creation information
    send_message = "{} Your mission ID for >{}< is: {}".format(ctx.author.mention, mission, mission_id)
    await ctx.send(send_message)

    # Creating a new table named with the unique mission_id
    sql = 'CREATE TABLE "{}" (id INTEGER NOT NULL PRIMARY KEY, mission_date TEXT)'.format(mission_id)
    cursor.execute(sql)
    sql = 'INSERT INTO "{}" (mission_date) VALUES ("{}")'.format(mission_id, date)
    cursor.execute(sql)

    # close connection to database
    conn.commit()
    conn.close()

def highest_mission_id():
    """
    Returning the highest mission_id.
    """
    conn = sqlite3.connect("slotlist.db")
    cursor = conn.cursor()

    # highest number of all mission_id will always be the highest not the next available
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
    # gets the slots from a file names slots.txt inside the bot folder
    file = open(os.getcwd() + "/slots.txt", "r")
    fileLines = file.readlines()

    conn = sqlite3.connect("slotlist.db")
    cursor = conn.cursor()
    slot_id = 1

    sql = 'UPDATE "{}" SET id = "{}"'.format(mission, len(fileLines))
    cursor.execute(sql)

    # every slot gehts two columns name of the slot and name of the player, with player be null at creating
    for x in fileLines:
        sql = 'ALTER TABLE "{}" ADD COLUMN s{}n text'.format(mission, slot_id)
        cursor.execute(sql)
        sql = 'UPDATE "{}" SET s{}n = "{}"'.format(mission, slot_id, x[0:-1])
        cursor.execute(sql)
        sql = 'ALTER TABLE "{}" ADD COLUMN s{} text'.format(mission, slot_id)
        cursor.execute(sql)
        slot_id = slot_id + 1

    # inform the dicord author for his successfully command
    send_message = "{} You successfully added {} slots for >{}<".format(ctx.author.mention, len(fileLines), mission_convert(mission))
    await ctx.send(send_message)

    conn.commit()
    conn.close()
    # add a channel to the missions category in discord
    await addmissionchannel(ctx, mission)

# if remote connection is not available for the discord membr who adds a mission, he can also create a slots.txt with this command
# argument have to be the output of the slotlist-editor.py or selfwriten with same data type
# data type of slots will be:
# each line is one slot starting with the first and ending with the last slot
# no empty lines inside the slotlist
# last character have to be a '\n' (a linebreak or slots have to be ended with a empty line)
# lines are groupname a comma and without a space the slotname eneded with a line break
# example> My Group 1-1,My Slot 1
@bot.command(name = "addSlotsT", help = "Adding the slots as .txt file inside the bot folder")
async def addSlotsT(ctx, slots: str):
    """
    Creating a .txt file inside the bot folder to prepare addSlots command with a discord command.
    Without the need to have access to the discord bot folder.
    """
    file = open(os.getcwd() + "/slots.txt", "w+")
    fileLines = slots.split("\n")
    del fileLines[-1]

    for i in fileLines:
        file.write(i + "\n")
    file.close()

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
        sql = 'SELECT mission_date FROM "{}"'.format(data[x][0])
        cursor.execute(sql)
        date = cursor.fetchall()[0][0]
        send_message = send_message + "{}: {} - {}\n".format(data[x][0], data[x][1], date)

    await ctx.send(send_message)


    conn.commit()
    conn.close()

#  bot commands can't be called from outside so the command just point to the actual function
@bot.command(name = "missioninfo", help = "List all available mission related informations")
async def missioninfo(ctx, mission: int):
    await missioninfofnc(ctx, mission, False)

async def missioninfofnc(ctx, mission: int, edit):
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

    sql = 'SELECT mission_date FROM "{}"'.format(mission)
    cursor.execute(sql)
    data = cursor.fetchall()
    time = data[0][0]

    sql = 'SELECT * FROM "{}"'.format(mission)
    cursor.execute(sql)
    data = cursor.fetchall()

    send_message = "{}: {}\n{}\n".format(mission, mission_convert(mission), time)

    group = ""
    j = 2 # j is the pointer to the slotname position starting with the third element in mission_id table
    for i in range(1, nslots + 1): # slots have to be counted for slot command
        group_name = data[0][j].split(",")[0]
        if group != group_name: # send a new title if a new group starts
            send_message = send_message + "\n**{}**:\n".format(group_name)
            group = group_name
        send_message = send_message + "{}: {}{}\n".format(i, data[0][j].split(",")[1], get_name(data, j + 1))
        j = j + 2 # every second element starting from third element is a slotname
    if edit: # if the message with slotlist is already sended to the mission channel just edit it
        m = await ctx.history().get(author__name = "Slotlist")
        await m.edit(content = send_message)
    else:
        await ctx.send(send_message)

    conn.commit()
    conn.close()

def get_name(data, i):
    """
    If a slot has a slotted player add " - Playername" to the slotname
    If not return nothing
    """
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

    # loop all slots if player is already slotted
    if already_slotted(ctx.author, mission):
        conn.commit()
        conn.close()
        send_message = "{} You are already slotted".format(ctx.author.mention)
        await ctx.send(send_message)
        return

    # check if slot is already taken
    sql = 'SELECT s{} FROM "{}"'.format(slot, mission)
    cursor.execute(sql)
    data = cursor.fetchall()
    slotdb = data[0][0]

    if slotdb == None:
        sql = 'UPDATE "{}" SET s{} = "{}"'.format(mission, slot, ctx.author)
        cursor.execute(sql)

        send_message = "{} You now have the slot #{} at >{}<".format(ctx.author.mention, slot, mission_convert(mission))
        await ctx.send(send_message)
    else:
        send_message = "{} Slot is already taken. I'm sorry".format(ctx.author.mention)
        await ctx.send(send_message)

    conn.commit()
    conn.close()
    await addmissionchannel(ctx, mission) # refresh mission information in the missions channel

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
        if data[0][(x * 2) + 1] == str(name):
            return True
    return False

@bot.command(name = "rslot", help = "Remove your assignment for a mission")
async def rslot(ctx, mission: int):
    """
    Connects to the database and checks all slots for the slotted player.
    And remove it.
    Returning with answering the client command.
    """
    conn = sqlite3.connect("slotlist.db")
    cursor = conn.cursor()

    # if no slot is taken by the player you can remove it
    if not already_slotted(ctx.author, mission):
        conn.commit()
        conn.close()
        send_message = "{} You don't have a slot".format(ctx.author.mention)
        await ctx.send(send_message)
        return
    else:
        sql = 'SELECT * FROM "{}"'.format(mission)
        cursor.execute(sql)
        data = cursor.fetchall()
        # loop from slot 1 to max(slot) == id in data[0][0] in mission id table
        for x in range(1, data[0][0] + 1):
            if data[0][(x * 2) + 1] == str(ctx.author):
                sql = 'UPDATE "{}" SET s{} = NULL'.format(mission, x)
                cursor.execute(sql)
                send_message = "{} You removed your assignment".format(ctx.author.mention)
                await ctx.send(send_message)
    conn.commit()
    conn.close()
    await addmissionchannel(ctx, mission) # refresh mission information in the missions channel

@bot.command(name = "aslot", help = "Assign player for a mission")
async def aslot(ctx, player, mission: int, slot: int):
    """
    Connects to the database and slot a player for a mission if available
    Equal to slot command but not executed by player, but someone else
    """
    conn = sqlite3.connect("slotlist.db")
    cursor = conn.cursor()

    if already_slotted(player, mission):
        conn.commit()
        conn.close()
        send_message = "{} Is already slotted".format(ctx.author.mention)
        await ctx.send(send_message)
        return
    else:
        sql = 'SELECT s{} FROM "{}"'.format(slot, mission)
        cursor.execute(sql)
        data = cursor.fetchall()
        slotdb = data[0][0]

        if slotdb == None:
            player = await find_target(ctx, str(player))
            sql = 'UPDATE "{}" SET s{} = "{}"'.format(mission, slot, player)
            cursor.execute(sql)

            send_message = "{} assigned {} to slot #{} at >{}<".format(ctx.author.mention, player.mention, slot, mission_convert(mission))
            await ctx.send(send_message)
        else:
            send_message = "{} Slot is already taken. I'm sorry".format(ctx.author.mention)
            await ctx.send(send_message)

    conn.commit()
    conn.close()
    await addmissionchannel(ctx, mission)

async def find_target(ctx, arg):
		"""
        Returns the player id.
        From string to member.
        Needed to be mentioned
        """
		if arg in ('everyone', 'all'):
			return discord.Object(id=0)

		return await MemberConverter().convert(ctx, arg)

async def addmissionchannel(ctx, mission):
    """
    Adds a channel after !addSlots
    """
    category = False
    channels = []
    chan = None
    cat = None
    name = mission_convert(mission)

    # is category available
    for x in ctx.guild.categories:
        if "missions" in str(x):
            category = True
            cat = x
            channels = x.text_channels
            break

    if not category:
        # create category
        server = ctx.message.guild
        cat = await server.create_category("missions")

    # is channel available
    if channels == []:
        server = ctx.message.guild
        chan = await server.create_text_channel("{}-{}".format(mission, name), category = cat)
        await missioninfofnc(chan, mission, False)
        return
    else:
        need = True
        for x in channels:
            if str(x) == "{}-{}".format(mission, name):
                chan = x
                need = False
                break
        if need:
            server = ctx.message.guild
            chan = await server.create_text_channel("{}-{}".format(mission, name), category = cat)
            await missioninfofnc(chan, mission, False)
            return
        await missioninfofnc(chan, mission, True)

def name_convert(name):
    """
    return will be name, but compatible with discord channel name restrictions
    """
    return name.replace(" ", "-").lower()

bot.run(token)
