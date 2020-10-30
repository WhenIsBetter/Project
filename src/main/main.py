from spm_bot.DiscordBot import DiscordBot

if __name__ == "__main__":
    TOKEN = open("../../deploy/token.txt", "r").read()

    bot = DiscordBot()
    print(f"Logged in and ready to go!")
    bot.run(TOKEN)
