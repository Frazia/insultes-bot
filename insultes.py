import discord
import argparse
from commands.insult import subparser_install as insult_subparser
from commands.insult import list_subparser_install as list_subparser

client = discord.Client()

def help_subparser(subparser):
    parser_help = subparser.add_parser(
        'help',
        help='Help',
    )
    parser_help.set_defaults(func=helper)

def helper(**kwargs):
    return {'msg': ['**/insult `username`\nlist `names`|`adjectives`\n/help**']}

SIMPLE_COMMANDS = [
    ('help', help_subparser),
    ('insult', insult_subparser),
    ('list', list_subparser),
]

COMMANDS = [
#('abuse', abuse_subparser)
]

# Override error class (not exiting anymore)
class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


# Generating parser
parser = ArgumentParser()

subparser = parser.add_subparsers(dest='main_command', help='The main command')
subparser.required = True

for command in SIMPLE_COMMANDS:
    command[1](subparser)

for command in COMMANDS:
    cmd_parser = subparser.add_parser(command[0])
    cmd_subparser = cmd_parser.add_subparsers(dest='sub_command', help='The {0} sub-command'.format(command[0]))
    command[1](cmd_subparser)


async def execute_command(message):
    try:
        cmd = message.content[1:].split(' ')

        commands = []
        for item in SIMPLE_COMMANDS:
            commands.append(item[0])
        for item in COMMANDS:
            commands.append(item[0])
        if cmd[0] not in commands:
            usage = 'Command "{}" not found.\nUse /help to see available commands'.format(cmd[0])
            await client.send_message(message.channel, usage)
            return

        argument = parser.parse_args(cmd)
        argument.message = message
        argument.client = client
        ret = argument.func(**vars(argument))
    except Exception as e:
        await client.send_message(message.channel, e)
        return

    if 'game' in ret:
        await client.change_presence(game=ret['game'])
    if 'status' in ret:
        await client.change_presence(status=ret['status'])

    if 'msg' in ret:
        if 'channel' in ret:
            await client.send_message(ret['channel'], ret['msg'])
        else:
            await client.send_message(message.channel, ret['msg'])
    return


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    if message.content.startswith('/'):
        await execute_command(message)

@client.event
async def on_message_edit(before, after):
    if after.author == client.user:
        return
    if after.content.startswith('/'):
        await execute_command(after)

@client.event
async def on_ready():
    print(client.user.name, ' ready !')
    print('------')

    now_playing = discord.Game(name='/help to see available commands')
    await client.change_presence(game=now_playing)


client.run('MzM3OTAyMzg1NDU4NDQ2MzQ2.DFNt4g.NOXenryxEq5IvDdhs44Ijd--a8U')
client.logout()
