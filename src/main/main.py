from DiscordBot import DiscordBot

if __name__ == "__main__":
    TOKEN = open("../../deploy/token.txt", "r").read()

    bot = DiscordBot(TOKEN)
    print(f"Logged in and ready to go!")
    bot.run()
