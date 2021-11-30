import discord
from discord.ext import commands, tasks
from discord.abc import PrivateChannel
from discord.utils import get
import os
import json
from random import randint

prefix = "."

client = commands.Bot(command_prefix=prefix,help_command=None)

print(f"Logged as {client}")

@client.command()
async def play(ctx,member : discord.Member = None):
    if member is None:
        await ctx.send(f"Missing argument (member) >> {prefix}play <@member>")
        return
    author = ctx.author
    guild = ctx.guild
    if author == member:
        await ctx.send("Can't invite yourself to duel!")
        return
    await ctx.send(f"{member.mention} do you want to join duel (Y/n)?")
    msg = await client.wait_for('message', check=lambda message: message.author == member, timeout=30)

    if msg.content != "y" and msg.content != "Y":
      await ctx.send("Duel canceled!")
      return 


    width = 19
    height = 10

    game = []
    border = ""

    for x in range(width):
        border += "⬜"
    game.append(border)
    for x in range(height-2):
        insideGame = "⬜"
        for x in range(width-2):
            insideGame += "⬛"
        insideGame += "⬜"
        game.append(insideGame)
    game.append(border)
    
    class pad1:
        l = []
        r = []


    class ball:
        x = round(width/2)
        y = round(height/2)

    class g:
        x = -1
        y = 1


    r = randint(1,2)
    r2 = randint(1,2)
    if r == 1:
        g.x = -1
    else:
        g.x = 1
    if r2==1:
        g.y = -1
    else:
        g.y = 1

    class score:
        a = 0
        b = 0
    scoreMsg = f"{ctx.author.mention}: {score.a} :x: {member.mention}: {score.b}"


    for x in range(round(height/2)-1,round(height/2)+1):
        pad = list(game[x])
        pad[2] = "⬜"
        pad[width-3] = "⬜"
        pad = ''.join(pad)
        game[x] = pad
        pad1.l.append(x)
        pad1.r.append(x)

    ball1 = list(game[round(ball.y)])
    ball1[round(ball.x)] = "⚪"
    ball1 = ''.join(ball1)
    game[x] = ball1

    game2 = "\n".join(game)
    #print(game)
    scores = await ctx.send(scoreMsg)
    send = await ctx.send(game2)
    id = send.id

    

    moveDown = []
    moveUp = []

    async def reset():
        for y in range(1,height-1):
            desk = list(game[y])
            for x in range(3,width-3):
                desk[x] = "⬛"
            desk = ''.join(desk)
            game[y] = desk
        ball.y = round(height/2)
        ball.x = round(width/2)

        desk = list(game[ball.y])
        desk[ball.x] = "⚪"
        desk = ''.join(desk)
        game[ball.y] = desk

        gameText = "\n".join(game)
        await send.edit(content=gameText)
        
        await scores.edit(content=f"{ctx.author.mention}: {score.a} :x: {member.mention}: {score.b}")

    async def moveBall():
        if ball.y >= height-2 or ball.y <= 1:
            g.y *= -1
        
        if ball.x >= width-4:
            g.x *= -1
            if ball.y not in pad1.r:
                g.y *= -1
                score.a += 1
                await reset()
                return
        if ball.x <= 3:
            g.x*=-1
            if ball.y not in pad1.l:
                g.y*=-1
                score.b += 1
                await reset()
                return

        for y in range(1,height-1):
            desk = list(game[y])
            for x in range(3,width-3):
                desk[x] = "⬛"
            desk = ''.join(desk)
            game[y] = desk

        ball.x += g.x 
        ball.y += g.y

        desk = list(game[ball.y])
        desk[ball.x] = "⚪"
        desk = ''.join(desk)
        game[ball.y] = desk


    async def update():
        try:

            await moveBall()
            gameText = "\n".join(game)
            await send.edit(content=gameText)
            await scores.edit(content=f"{ctx.author.mention}: {score.a} :x: {member.mention}: {score.b}")
            for reactions in send.reactions:
                async for user in reactions.users():
                    if user != client.user:
                        await send.remove_reaction(reactions, user)
        except Exception as e:
            print(e)


    async def clear(side):
        if side == "L":
            for x in range(1,height-1):
                pad = list(game[x])
                pad[2] = "⬛"
                pad = ''.join(pad)
                game[x] = pad
        else:
            for x in range(1,height-2):
                pad = list(game[x])
                pad[width-3] = "⬛"
                pad = ''.join(pad)
                game[x] = pad
    async def moveMeUp(side):
        
        
        try:
            if side == "L":
                if pad1.l[0] <= 1:
                    return
                await clear(side)
                tempL = []
                for x in pad1.l:
                    tempL.append(x-1)
                pad1.l = tempL
                for x in pad1.l:
                    pad = list(game[x])
                    pad[2] = "⬜"
                    pad = ''.join(pad)
                    game[x] = pad
            else:  
                return
        except Exception as e:
            print(e)

    async def moveMeDown(side):
        
        
        
        try:
            if side == "L":
                if pad1.l[len(pad1.l)-1] >= height-2:
                    return
                await clear(side)
                tempL = []
                for x in pad1.l:
                    tempL.append(x+1)
                pad1.l = tempL
                for x in pad1.l:
                    pad = list(game[x])
                    pad[2] = "⬜"
                    pad = ''.join(pad)
                    game[x] = pad
                    
            else:  
                if pad1.r[len(pad1.r)-1] >= height-2:
                    return
                await clear(side)
                tempR = []
                for x in pad1.r:
                    tempR.append(x+1)
                pad1.r = tempR
                for x in pad1.r:
                    pad = list(game[x])
                    pad[width-3] = "⬜"
                    pad = ''.join(pad)
                    game[x] = pad
                    
        except Exception as e:
            print(e)

    def check(reaction,user):
        return (user == ctx.author or user == member) and str(reaction.emoji) == "✅"

    await send.add_reaction("⬆️")
    await send.add_reaction("⬇️")
    await send.add_reaction("✅")
    send = await send.channel.fetch_message(send.id)
    while True:
        moveUp = []
        moveDown = []
        try:
            await client.wait_for('reaction_add', check=check)
            for reactions in send.reactions:
                if str(reactions.emoji) == "⬆️":
                    user_list = [user async for user in reactions.users() if user != client.user]
                    for user in user_list:
                        if user == ctx.author:
                            await moveMeUp("L")
                        elif user == member:
                            await moveMeUp("R")

                elif str(reactions.emoji) == "⬇️":
                    user_list = [user async for user in reactions.users() if user != client.user]
                    for user in user_list:
                        if user == ctx.author:
                            await moveMeDown("L")
                        elif user == member:
                            await moveMeDown("R")
        except Exception as e:
            continue
            print(e + "ERROR2")
        await update()

# Invalid command (ERROR)
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing argument!")


with open('token.txt','r') as f:
    token = f.read()
    client.run(token)