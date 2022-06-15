import discord
from discord.ext import commands
from keep_alive import keep_alive
from replit import db
import random
import time

client = commands.Bot(command_prefix='!', help_command=None)
channel = client.get_channel(975987138074128404)
user = []
user_name = []
card = [[],[],[],[]]
name = "Tiger Roar" #bot name
st = "老虎來囉"
ok = 0 #playing or not 
on = 0 #0 stands for joining, 1-> call, 2-> play
u = 0 #pass count
now = 0 #now pos
max = 0 #max weight
king = -1 #king num
tar = 1 #target for win
last = 1 #last call
big_string = "" #last call
start = 0 #start
first_col = 0 #the first
tar_1 = 0 #the first target
tar_2 = 0 #
score_1 = 0 #the first score
score_2 = 0 #
bigger = 0#whose card biggest
round = 0 #round
cot = 0

#db['update log']=[]
#db['update log'].append(["v1.01","Fix the initialize bug"])
#declare commands
@client.command()
async def help(ctx):
    #inlime false
    try:
      text=discord.Embed(title=help, url="https://Pi.enchichi.repl.co")
      text.add_field(name="!start", value="Start a round", inline=False)
      text.add_field(name="!join", value="join a round", inline=False)
      text.add_field(name="!com + [abbreviation + number]", value="command",   inline=False)
      text.add_field(name="col_abbreviations", value="C=clubs\nD=diamonds\nH=hearts\nS=spades\nN=no king\nP=pass", inline=False)
      text.add_field(name="!update_log", value="Show update log.", inline=False)
      text.add_field(name="!help", value="Show this message.", inline=False)
      await ctx.send(embed = text)
    except:
      print("err")

@client.command()
async def update_log(ctx):
    #inlime false
    try:
      text=discord.Embed(title="update_log")
      for i in db['update log']:
        text.add_field(name=i[0], value=i[1], inline=False)
      await ctx.send(embed = text)
    except:
      print("err")
      
@client.command()
async def start(ctx):
    global ok, user, user_name, channel, on
    if(ok == 0):
      await ctx.channel.send(embed = discord.Embed(title=name,
                             description="Use !join to participate."))
      user.clear()
      user_name.clear()
      ok = 1
      on = 0      
    else:
      ok = 0
      await ctx.channel.send(embed = discord.Embed(title=name,
                             description="The round is canceled"))
      
@client.command()
async def join(ctx):
    try:
      global user, channel, ok, on, max, u, name, now
      if(ok == 0):
        await ctx.channel.send(embed = discord.Embed(title=name,
                             description="You haven't start a round.")) 
        return 
      if(len(user) == 4):
        await ctx.channel.send(embed = discord.Embed(title=name,
                             description="Full now, sorry.")) 
        return
      user_name.append(str(ctx.author.name))
      user.append(ctx.author)
      await ctx.channel.send(embed = discord.Embed(title=name,
                             description="Succeed! "+user_name[len(user)-1]+" ,You are player "+str(len(user)))) 
      if(len(user) == 4):
        on = 1
        await send()
        u = 3
        max = 0
        now = 0
        await ctx.channel.send(embed = discord.Embed(title=name,
                             description="Now player "+user_name[0]+" (Player 1) start first. Use command: com ")) 
    except:
      await ctx.channel.send(embed = discord.Embed(title=name,
                             description="Exception 000\nInternal Error, please contact admin.")) 
    #:clubs: :diamonds:  :hearts: :spades: 

@client.command()
async def com(ctx,arg):
  global user, now, ok, on, name, start, round, tar, tar_1, tar_2, score_1, score_2, max, cot
  try:
    if(ok == 0):
      await ctx.channel.send(embed = discord.Embed(title=name,description="You haven't start a round.")) 
      return 
    if(on == 0):
      await ctx.channel.send(embed = discord.Embed(title=name,description="Please join first.")) 
      return 
    if(user[now] != ctx.author):
      await ctx.channel.send(embed = discord.Embed(title=name, description="It's not your turn.")) 
      return 
    if(on == 1):
      await call(ctx,arg.strip())
      if(u == 0):
        start = (last + 1) % 4
        now = start
        round = 1
        max = 0
        score_1 = score_2 = 0
        if(last == 0 or last == 2):
          tar_1 = 6 + tar
          tar_2 = 8 - tar
        if(last == 1 or last == 3):
          tar_2 = 6 + tar
          tar_1 = 8 - tar
        await ctx.channel.send(embed = discord.Embed(title=name,description="Now start from player "+str(now+1)+" : "+user_name[now])) 
        on = 2
        cot = 0
        return 
    if(on == 2):
      await play_card(ctx,arg.strip())
      if(cot == 4):
        if(bigger == 0 or bigger == 2):
          score_1 += 1
        else:
          score_2 += 1
        await ctx.channel.send(embed = discord.Embed(title=name,
description="Round "+str(round)+" has ended.\nCurrent 1P & 3P score is: " + str(score_1)+"/"+str(tar_1)+"\nCurrent 2P & 4P score is: "+ str(score_2)+"/"+str(tar_2)))
        round += 1
        if(round == 14):
          ok = on = 0
          return 
        now = bigger
        start = bigger
        max = 0
        time.sleep(2)
        await send()
        time.sleep(2)
        cot = 0
        await ctx.channel.send(embed = discord.Embed(title=name,
description="Round "+str(round)+" has start! First player is "+str(now+1)+" : "+user_name[now]))
      
  except:
    await ctx.channel.send(embed = discord.Embed(title=name,description="Exception 001\n Internal Error, please contact admin.")) 

@client.event
async def play_card(ctx,string):
    global user, card, max, king, tar, now, name, start, bigger, now, first_col, cot
    try:
      a = string[0]
      b = int(string[1:])
      sym = await decode(a)
      if(sym == -1 or sym == 5 or b > 13 or b < 1):
        await ctx.channel.send(embed = discord.Embed(title=name, description="Exception 201\nFormat is wrong.")) 
        return
      if(now != start and sym != first_col):
        for i in card[now]:
          if(i//100 == first_col):
            await ctx.channel.send(embed = discord.Embed(title=name,
                             description="Exception 202\nYour command is wrong.")) 
            return 
      pri = 100 * sym + b
      find = False
      print("111")
      print(now)
      for i in card[now]:
        if(i == pri):
          find = True
          card[now].remove(pri)
      if(find == False):
        await ctx.channel.send(embed = discord.Embed(title=name,description="Exception 203\nYour command is wrong.")) 
        return
      if(now == start):
        first_col = sym
        max = 0
      if(sym == king):
        sym = 100000
      elif(sym != first_col):
        sym= -100000
      if(b == 1):
        b = 14
      pri = sym + b
      if(pri > max):
         max = pri 
         bigger = now
      now += 1
      now %= 4
      cot += 1
      print("111")
      if(cot != 4):await ctx.channel.send(embed = discord.Embed(title=name, description=("Next player is player "+str(now+1)+" : "+user_name[now])))
      #+str+"\nNext player: "+str(now+1)
    except:
      await ctx.channel.send(embed = discord.Embed(title=name,description="Exception 204\nPlease send again. The format might be wrong.")) 
      return
  
  
@client.event
async def call(ctx,string):
    global user, card, u, max, king, tar, now, name, last, big_string
    
    if(string.strip()=="P"):
      if(max == 0):
        await ctx.channel.send(embed = discord.Embed(title=name,
                             description="Exception 100\nSince you are the first player, you can't not use pass this time. Please send again.")) 
        return
      u -= 1
      now += 1
      now %= 4
      if(u == 0):
        await ctx.channel.send(embed = discord.Embed(title=name,description="Now the final contract is "+big_string+" by player "+str(last+1)))                    
      else: 
        await ctx.channel.send(embed = discord.Embed(title=name, description=("Now the contract is "+big_string+" by player "+str(last+1)+"\nNext player is "+str(now+1))))
      return
    u = 3
    try:
      a = string[0]
      b = int(string[1:])
      sym = await decode(a)
      if(sym == -1  or b>7 or b<1):
        await ctx.channel.send(embed = discord.Embed(title=name,
                             description="Exception 101\nFormat is wrong.")) 
        return
      pri=sym+1+(b-1)*100
      if(pri <= max):
        await ctx.channel.send(embed = discord.Embed(title=name,
                             description="Exception 102\nContract is not big enough.")) 
        return  
      max = pri
      king = sym
      tar = b  
      last = now
      now += 1
      now %= 4
      big_string = string
      await ctx.channel.send(embed = discord.Embed(title=name,                        description=("Now the contract is "+big_string+" by player "+str(last+1)+"\nNext player is "+str(now+1)))) 
      #+str+"\nNext player: "+str(now+1)
    except:
      await ctx.channel.send(embed = discord.Embed(title=name,
                             description="Exception 103\nPlease send again. The format might be wrong.")) 
      return
  
@client.event
async def decode(a):
    s = -1 
    if(a == "C"):
      s = 0
    if(a == "D"):
      s = 1
    if(a == "H"):
      s = 2
    if(a == "S"):
      s = 3
    if(a == "N"):
      s = 4
    return s
      
@client.event
async def send():
    card_is_ok = False
    global user, card 
    o = []
    while(card_is_ok == False):
      if(on == 1):await shuff()
      card_is_ok = True
      out = ""
      o.clear()
      for i in range(4):
        out = ""
        cnt = 0
        one_cnt = 0
        card[i].sort()
        for k in range(4):
          if k==0: out+="C :clubs:" #clubs
          if k==1: out+="D :diamonds:" #diamond
          if k==2: out+="H :hearts:" #hearts
          if k==3: out+="S :spades:" #spades
          for j in card[i]:
            if(j//100==k):
              a = j%100
              out+=str(a)
              out+=" "
              if(a == 11):cnt+=1
              if(a == 12):cnt+=2
              if(a == 13):cnt+=3
              if(a == 1):
                cnt+=4
                one_cnt+=1
          out+="\n" #T
        if(on == 1 and (one_cnt == 4 or cnt < 4)):
          card_is_ok = False
        o.append(discord.Embed(title=name,
                             description=out))
    for i in range(4):
      await user[i].send(embed = o[i]) 

@client.event
async def shuff():
    global card
    sh = []
    for i in range(0,4):
      card [i] = []
      for j in range(1,14):
        sh.append(i*100+j)
    random.shuffle(sh)
    for i in range(52):
      card[i%4].append(sh[i])

@client.event
async def on_ready():
    global st
    game = discord.Game(st)
    await client.change_presence(status=discord.Status.online, activity=game)

keep_alive()
client.run(db['token'])

