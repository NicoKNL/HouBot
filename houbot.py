import discord
import discord.ext.commands.bot as discordbot
import logging
import asyncio
from random import choice
from time import strftime, localtime, sleep
import datetime
import urllib.request
import json

logging.basicConfig(level=logging.INFO)

print(discord.version_info)
client = discord.Client()
TOKEN = ""  # Your bot OAUTH code here.


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
            s = s.format(format + "\n{}")
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
        self.response_time = 1.0 # Response time of the bot in seconds
        self.max_response_time = 2.0 # For a dynamic response time approach, see HouBot.message()

    @Bot.action
    async def help(self, args, mobj):
        """
        Return a link to a command reference sheet

        If you came here from !help help, you're out of luck.
        """
        output = "Hey there! Thank you for using the help functionality.\n\n"
        output += "##############################################################################\n"
        output += "# Don't forget to run the more server related commands in the actual server! #\n"
        output += "##############################################################################\n\n"
        output += "Here are the available commands:\n\n"

        for c in [f"{k}" for k in self.ACTIONS.keys()]:
            output += f"        {c}\n"

        output += "\n For more info on each command, use '!command help'"
        return await self.message(mobj.author, self.pre_text(output))

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
        Example: !log Your message here.
        """
        return self.logger("Testing!")

    @Bot.action
    async def channel_name(self, args, mobj):
        """
        Get the info for the current channel.
        Example: !channel_name
        """
        return await self.message(mobj.channel, self.pre_text(mobj.channel.name))

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

    @Bot.action
    async def embed_test(self, args, mobj):
        """Rich embed test"""
        embed = discord.Embed(title="title ~~(did you know you can have markdown here too?)~~",
                              colour=discord.Colour(0xadd899), url="https://vimeo.com/108650530",
                              description="this supports [named links](https://discordapp.com) on top of the previously shown subset of markdown. ```\nyes, even code blocks```",
                              timestamp=datetime.datetime.utcfromtimestamp(1494093265))

        embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")
        embed.set_thumbnail(url="https://cdn.discordapp.com/embed/avatars/0.png")
        embed.set_author(name="author name", url="https://discordapp.com",
                         icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
        embed.set_footer(text="footer text", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")

        embed.add_field(name="🤔", value="some of these properties have certain limits...")
        embed.add_field(name="😱", value="try exceeding some of them!")
        embed.add_field(name="🙄",
                        value="an informative error should show up, and this view will remain as-is until all issues are fixed")
        embed.add_field(name="<:thonkang:219069250692841473>", value="???")

        await self.client.send_message(mobj.channel, "this `supports` __a__ **subset** *of* ~~markdown~~ 😃 ```js\nfunction foo(bar) {\n  console.log(bar);\n}\n\nfoo(1);```", embed=embed)

    @Bot.action
    async def change_name(self, args, msg):
        """
        Change someones name
        """
        await self.message(msg.channel, self.pre_text(str(args)))
        user = discord.utils.get(msg.server.members, name=args[0])
        # member_role = discord.utils.get(msg.server.roles, name="Member")

        await self.client.change_nickname(user, args[1])

    @Bot.action
    async def kys(self, args, mobj):
        """Kill switch"""
        self.logger(self.pre_text("Shutting down."))
        await self.message(mobj.channel, self.pre_text("Shutting down."))
        await self.client.logout()

    async def vimeo_helper(self, mobj, vimeo_id=None):
        """Rich embed test"""
        # import pprint

        with urllib.request.urlopen(f"https://vimeo.com/api/v2/video/{vimeo_id}.json") as url:
            data = json.loads(url.read().decode())
            # pprint.pprint(data)
            v_title = data[0]["title"]
            v_thumbnail = data[0]["thumbnail_large"]
            v_url = data[0]["url"]
            v_author = data[0]["user_name"]

        embed = discord.Embed(title=v_title,
                              url=v_url)
        embed.add_field(name=v_author, value=v_url)
        embed.set_image(url=v_thumbnail)

        await self.client.send_message(mobj.channel, embed=embed)

    async def set_status(self, string):
        """Set the client's presence via a Game object"""
        return await self.client.change_presence(game=discord.Game(name=string))

    async def message(self, channel, msg):
        """
        Shorthand version of client.send_message.
        This way we don't have to type 'self.client.send_message' all the time
        """
        await self.client.send_typing(channel)

        # Response time logic
        # Everybody has to spend at least a second or two typing their message
        # Thus we add some 'response time' as well to make the bot feel more like a natural user.

        # Static response time
        # sleep(self.response_time)

        # Dynamic response time based on message length. Oddly enough, longer messages take longer to type
        msg_length = len(msg)
        response_time = msg_length * 0.005 # self.character_time ?
        self.logger(response_time)
        if response_time > self.max_response_time:         # But let's also have a max response time
            response_time = self.max_response_time
        sleep(response_time)
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
            ## Filtering out the bot's own messages ##
            if msg.author == self.client.user:
                return

            ## Auto-mod based on name ## ! TEMPORARY
            mods = ["toadstorm", "siams", "probiner", "mestela", "houbot"]
            user = msg.author
            user_name = user.name.lower()
            if msg.channel.name == "introductions":
                for mod_name in mods:
                    self.logger(user_name)
                    if user_name in mod_name:
                        mod_role = discord.utils.get(msg.server.roles, name="Moderator")
                        try:
                            await self.client.add_roles(user, mod_role)
                            return
                        except Exception as e:
                            self.logger(f"{e}")
                            return

            ## Exctracting the arguments ## # TODO: validation. User can start a sentence with {self.PREFIX} without wanting a command. Eg. "!!! omg !!! what a render !!!"
            args = msg.content.strip().split(" ")
            key = args.pop(0).lower()  # messages sent can't be empty

            ## Implementation of the introductions-message -> member-role ##
            if msg.channel.name == "introductions":
                user = msg.author
                user_roles = user.roles

                for role in user_roles:
                    self.logger(role)

                if len(user_roles) == 1 and user_roles[0].name == "@everyone":
                    member_role = discord.utils.get(msg.server.roles, name="Member")
                    try:
                        await self.client.add_roles(user, member_role)
                    except Exception as e:
                        self.logger(f"{e}")
                        return

            ## Implementation of the vimeo thumbnail embedder ##
            vimeo_flag = "https://vimeo.com" # TODO: regex matching please. - optional = ["http", "https", "www", ".", "//"], must have = ["vimeo.com", 10 digits]
            vimeo_url = ""
            for arg in args:
                if arg.startswith(vimeo_flag) and arg[-1] in "0123456789":
                    vimeo_url = arg

            if vimeo_url:
                vimeo_id = vimeo_url.rpartition("/")[-1]
                await self.vimeo_helper(msg, vimeo_id=vimeo_id)

            ## Catching the keyword commands ##
            if key.startswith(self.PREFIX):  # filter out messages that aren't commands.
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

