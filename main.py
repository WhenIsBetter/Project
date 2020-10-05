import discord


TOKEN = open("token.txt", "r").read()

client = discord.Client()


@client.event
async def on_ready():
    print("discord bot running!")


@client.event
async def on_message(message):
    print(f"--message info--\n{message.channel}: {message.author}: {message.author.name}: {message.content}\n----")
    if "!test" in message.content.lower():
        await message.channel.send('Hello, World!')

client.run(TOKEN)
