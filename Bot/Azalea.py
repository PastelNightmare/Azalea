import discum
from discord.ext import commands
import time
import asyncio

from Variables.config import *
from Variables.vars import *
from Utils.lists import *
from Utils.logging import *
from Objects.Mod import Moderator

User = discum.Client(token=USERTOKEN)
User.gateway.log = {"console":False, "file":False}
User.log = {"console":False, "file":False}
Bot = commands.Bot(command_prefix=BOTPREFIX, case_insensitive=True)



@User.gateway.command
def Bloom(resp):
	if resp.event.ready_supplemental:
		User.gateway.checkGuildMembers(Guild, List, keep="all")
	if resp.event.guild_members_chunk and User.gateway.finishedGuildSearch(Guild, userIDs=List):
		User.gateway.close()

@Bot.event
async def on_ready():
    User.gateway.run()
    await FillModStatus()
    asyncio.get_event_loop().create_task(Ping())

@Bot.command(name="status", brief="Fetches total amount of online moderators")
async def Status(ctx):
    i = 0
    for Jannie in Jannies:
        if Jannie.Status != "offline":
            i+=1
    
    string=""
    if i == 0:
        string="There are no currently online moderators."
    elif i == 1:
        string="There is only 1 online moderator."
    else:
        string=f"There are {i} currently online moderators"

    await Notify(string)

async def Notify(message):
	channel = Bot.get_channel(CHANNELID)
	await channel.send(message)

async def Ping():
    while True:
        Log(0, "Bloom")
        User.gateway.run()
        for i in range(len(List)):
            try:
                what = User.gateway.session.guild(Guild).members[List[i]]
                tmp = GetObject(what)
                if tmp.Status != Jannies[i].Status:
                    Log(1, f"{tmp.Username} ({tmp.Identity}) changed status to {tmp.Status}. Previously was {Jannies[i].Status}. {(tmp.Timestamp-Jannies[i].Timestamp)} has elapsed.")
                    Jannies[i] = tmp
                    await Notify(f"{tmp.Username} ({tmp.Identity}) is now {tmp.Status}")
                await asyncio.sleep(Refresh)
            except KeyError:
                Log(1, f"Cant find {Jannies[i].Username}! Removing from list!")
                List.pop(i)
                Jannies.pop(i)


def FillModList():
    global List
    List=[]
    Templist=[]
    UserIDList=[]

    if AUTO == True:
        RoleList = SortRoles(User.getGuildRoles(Guild).content.decode())
        for i in range(len(RoleList)):
            if (CheckJanitorPerms(int(RoleList[i]["permissions"])) == True):
                Templist.append(RoleList[i]["id"])
    else:
        Templist = ModRoles
    
    for RoleId in Templist:
        Log(0, f"Getting UserID's for {RoleId}")
        UserIDList += Filter(User.getRoleMemberIDs(Guild, RoleId).content.decode())
        time.sleep(3.5)

    [List.append(x) for x in UserIDList if x not in List]

    if len(List) == 0:
        Log(4, "List is empty! Check Role IDs!")
        exit(1)

async def FillModStatus():
    for i in range(len(List)):
        Janny = User.gateway.session.guild(Guild).members[List[i]]
        Obj = GetObject(Janny)
        Jannies.append(Obj)
        Log(0, f"Queried {i}, got \"{Obj.Username} ({Obj.Identity}) is {Obj.Status}\"")
        await Notify(f"{Obj.Username}, ({Obj.Identity}) is {Obj.Status}")
        time.sleep(0.8)
    await Notify(f"Azalea started - tracking {len(List)} moderators total.")

def Init():
    FillModList()
    Kickstart()

def Kickstart():
    Bot.run(BOTTOKEN)


