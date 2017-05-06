import discord
import logging
import asyncio
from random import choice
from time import strftime, localtime

logging.basicConfig(level=logging.INFO)

print(discord.version_info)
client = discord.Client()
TOKEN = "" # Your bot OAUTH code here.

class Bot(object):
    """
    The main Bot class for all bots to inherit from
    The Bot class holds any and most static variables to use
    across all the bots
    """

    # BOT_FOLDER = "botdata"
    # KEY_FOLDER = "keys"
    # SHARED = "shared"
    LOGSTR = "[\033[38;5;{3}m{0:<12}\033[0m @ {1}] {2}"
    ACTIONS = dict()
    PREFIX = "!"


    # # Static methods will come first
    # @staticmethod
    # def _make_folder(path):
    #     if not path.is_dir() and not path.is_file():
    #         path.mkdir()
    #         return True
    #     return False

    @staticmethod
    def _create_logger(bot_name):
        """
        Create a pretty-format printer for bots to use
        Bots will use colors in the range of 16-256 based on their hash modulo
        """
        color = 16 + (hash(bot_name) % 240)
        def logger(msg):
            print(Bot.LOGSTR.format(bot_name, strftime("%H:%M%S", localtime()), msg, color))
            return True
        return logger

    # @staticmethod
    # def _create_filegen(bot_name):
    #     """
    #     Create a function to generate file Paths for us
    #     If no filename was given, yield the path to the folder instead
    #     """""
    #     Bot._make_folder(Path(Bot.BOT_FOLDER))
    #     Bot._make_folder(Path(Bot.BOT_FOLDER, bot_name))
    #     def bot_file(filename=None):
    #         if filename is None or filename == "":
    #             return Path(Bot.BOT_FOLDER, bot_name)
    #         return Path(Bot.BOT_FOLDER, bot_name, filename)
    #     return bot_file

    # @staticmethod
    # def _read_file(path):
    #     if not path.is_file():
    #         raise IOError
    #     with open(path, 'r') as f:
    #         return f.read()
    #     return None

    @staticmethod
    def pre_text(msg, lang=None):
        """
        Encapsulate a string in a <pre> container
        """
        s = "```{}```"
        if lang is not None:
            s = s.format(format+"\n{}")
        return s.format(msg.rstrip().strip("\n").replace("\t", ""))

    # Instance methods go below __init__()
    def __init__(self, name):
        self.name = name
        self.logger = self._create_logger(self.name)

    # def read_key(self):
    #     """
    #     Read a bot's keyfile to get it's token/webhook link
    #     """
    #     return Bot._read_file(Path(self.KEY_FOLDER, f"{self.name}.key")).strip("\n")

    @staticmethod
    def action(function):
        """
        Decorator to register functions into the action map.

        This is bound to static as we can't use an instance object's method as a decorator.
        could be a classmethod, but who cares
        """
        if callable(function):
            if function.__name__ not in Bot.ACTIONS:
                Bot.ACTIONS[f"{Bot.PREFIX}{function.__name__}"] = function
                return True
        return function



class HouBot(Bot):
    STATUS = "Hello, this is HouBot calling."

    def __init__(self):
        super(HouBot, self).__init__("HouBot")
        self.actions = dict()
        self.client = discord.Client()
        self.token = TOKEN

    @Bot.action
    async def help(self, args, mobj):
        """
        Return a link to a command reference sheet
        
        If you came here from !help help, you're out of luck.
        """
        output = "Thank you for choosing HouBot for your channel\n"
        output += "Here are the available commands\n\n"

        for c in [f"{k}" for k in self.ACTIONS.keys()]:
            output += f"* {c}\n"

        output += "\n For more info on each command, use '!command help'"
        return await self.message(mobj.channel, self.pre_text(output))

    @Bot.action
    async def status(self, args, mobj):
        """
        Change the bot's status to a given string
        Example: !status haha you are dumb
        """
        return await self.set_status(" ".join(args))

    @Bot.action
    async def coin(self, args, mobj):
        """
        Do a coin flip
        Example: !coin
        """
        return await self.message(mobj.channel, choice([":monkey:", ":snake:"]))

    @Bot.action
    async def log(self, args, mobj):
        """
        Force a log output.
        Example: !log You're message here.
        """
        return self.logger("Testing!")

    @Bot.action
    async def channel_name(self, args, mobj):
        """
        Get the info for the current channel.
        Example: !channel_name
        """
        return await self.message(mobj.channel, self.pre_text(mobj.channel.channel.name))

    @Bot.action
    async def server_name(self, args, mobj):
        """
        Get the info for the current server.
        Example: !server_name
        """
        return await self.message(mobj.channel, self.pre_text(mobj.channel.server.name))

    @Bot.action
    async def create_channel(self, args, mobj):
        """
        Get the info for the current server.
        Example: !create_channel cloaks-room text
        """
        channel_types = {"text": discord.ChannelType.text,
                         "voice": discord.ChannelType.voice,
                         "private": discord.ChannelType.private}
        channel_name = args[0]
        channel_type = channel_types[args[1]]

        all_channels = [c.name for c in self.client.get_all_channels()]
        if channel_name in all_channels:
            return await self.message(mobj.channel, self.pre_text(f"Channel '{channel_name}' already exists."))

        await self.client.create_channel(mobj.server, channel_name, type=channel_type)

    @Bot.action
    async def list_channels(self, args, mobj):
        """List all the current channels"""
        all_channels = [c.name for c in self.client.get_all_channels()]
        msg_head = "Here is an overview of all the current channels: \n\n"
        msg_list = [f"* {channel_name}\n" for channel_name in all_channels]
        msg = [msg_head] + msg_list
        self.logger([msg_head])
        self.logger(msg_list)
        self.logger(msg)
        return await self.message(mobj.channel, self.pre_text("".join(msg)))

    async def set_status(self, string):
        """Set the client's presence via a Game object"""
        return await self.client.change_presence(game=discord.Game(name=string))

    async def message(self, channel, msg):
        """
        Shorthand version of client.send_message.
        This way we don't have to type 'self.client.send_message' all the time
        """
        return await self.client.send_message(channel, msg)

    def display_no_servers(self):
        """
        Iff the bot isn't connected to any servers, show a link that will let you
        add the bot to one of your current servers.
        """
        if not self.client.servers:
            self.logger(f"Join link: {discord.utils.oauth_url(self.client.user.id)}")
        return

    def event_ready(self):
        """Change this event to change what happens on login"""
        async def on_ready():
            print("------- Log\n")
            self.logger(f"Logged in as: {self.client.user.name}")
            self.logger(f"ID: {self.client.user.id}")
            self.logger(" ")
        return on_ready

    def event_error(self):
        """Change this for better error logging if needed"""
        async def on_error(msg, *args, **kwargs):
            self.logger(f"Discord error: {msg}")
            self.logger(f"- args: {args}")
            self.logger(f"- kwargs: {kwargs}")
        return on_error

    def event_message(self):
        "Change this to change overall on message behavior"
        async def on_message(msg):
            if msg.author == self.client.user:
                return
            # self.logger(f"Message: {msg.content}")
            args = msg.content.strip().split(" ")
            key = args.pop(0).lower() # messages sent can't be empty
            # self.logger(f"Actions: {self.ACTIONS}")
            if key.startswith(self.PREFIX): # filter out messages that aren't commands.
                self.logger(f"Key registered: {key}")
                # self.logger(f"Args: {args}")
                if key in self.ACTIONS:
                    if len(args) >= 1:
                        if args[0].lower() == "help":
                            return await self.message(
                                msg.channel,
                                self.pre_text(
                                    f"Help for '{key}':{self.ACTIONS[key].__doc__}"
                                )
                            )
                    try:
                        return await self.ACTIONS[key](self, args, msg)
                    except Exception as e:
                        self.logger(e)
                        return
                elif key not in self.ACTIONS:
                    return await self.message(msg.channel, self.pre_text("Command not recognized."))
        return on_message

    def setup_events(self):
        """
        Set up all events for the bot.
        You can override each event_*() method in the class def
        """
        self.client.event(self.event_message())
        self.client.event(self.event_error())
        self.client.event(self.event_ready())

    def run(self):
        """
        Main event loop.
        Set up all Discord client events en then run the loop.
        """
        self.setup_events()
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.client.start(self.token))
        except Exception as e:
            print(f"Caught an exception: {e}")
        except SystemExit:
            print("System Exit signal")
        except KeyboardInterrupt:
            print("Keyboard Interrupt signal")
        finally:
            print(f"{self.name} quitting...")
            loop.run_until_complete(self.client.logout())
            loop.stop()
            loop.close()
            quit()
        return

if __name__ == "__main__":
    bot = HouBot()
    bot.run()

