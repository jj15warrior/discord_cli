import requests
import click
import json
from types import SimpleNamespace

click.echo(click.style('Currently you can only log in using token', bg='blue', fg='red', blink=True, bold=True))
token = input("token: ")

head = {
    "Authorization": token
}

resp = requests.get("http://discord.com/api/users/@me", headers=head)
if resp.status_code != 200:
    print("error. status code: ", resp.status_code)
    exit()
user = json.loads(resp.content, object_hook=lambda d: SimpleNamespace(**d))
print("logged in as: ", user.username + "#" + user.discriminator)

lastcommand = 0
scope = 0
channelscope_exists = False
while 1:
    command = input("discord-cli>>")
    if (command == "help"):
        print("""
        dms - list dms
        mass_dms - list group dms
        guilds - list servers
        goto - choose dm / server to move to
        channels - list channels in current server
        back - go back from server/dm
        history <x> - check last x messages in current channel
        send - write in current channel
        reply <x> - reply to message.
        unread_dm - show unread dms
        unread_guilds - show unread servers
        help - show this help
        send_file - send file to current channel
        """)
        lastcommand = 0
    if (command == "dms"):
        dms_unparsed = requests.get("http://discord.com/api/users/@me/channels", headers=head)
        if dms_unparsed.status_code != 200:
            print("error code: ", dms_unparsed.status_code)
            exit()
        dms = json.loads(dms_unparsed.content, object_hook=lambda d: SimpleNamespace(**d))
        index = 1

        for dm in dms:
            if dm.recipients != []:
                if len(dm.recipients) == 1:
                    print(str(index) + ": " + dm.recipients[0].username)
            index = index + 1
        lastcommand = 1

    if command == "mass_dms":
        dms_unparsed = requests.get("http://discord.com/api/users/@me/channels", headers=head)
        if dms_unparsed.status_code != 200:
            print("error code: ", dms_unparsed.status_code)
            exit()
        dms = json.loads(dms_unparsed.content, object_hook=lambda d: SimpleNamespace(**d))
        index = 1
        for dm in dms:
            if dm.recipients != []:
                if len(dm.recipients) > 1:
                    print(index, end=": ")
                    for recipient in dm.recipients:
                        print(recipient.username, end="; ")
                    print()
            index = index + 1
        lastcommand = 2

    if command == "guilds" or command == "servers":
        guilds_unparsed = requests.get("http://discord.com/api/users/@me/guilds", headers=head)
        if guilds_unparsed.status_code != 200:
            print("error code: ", guilds_unparsed.status_code)
            exit()
        guilds = json.loads(guilds_unparsed.content, object_hook=lambda d: SimpleNamespace(**d))
        index = 0
        for guild in guilds:
            index = index + 1
            print(str(index) + ": " + guild.name)
        lastcommand = 3

    if command == "channels":
        lastcommand = 4
        channels_unparsed = requests.get("https://discord.com/api/guilds/" + scopeuser.id + "/channels", headers=head)
        if channels_unparsed.status_code != 200:
            print("error code: ", channels_unparsed.status_code)
            exit()
        channels = json.loads(channels_unparsed.content, object_hook=lambda d: SimpleNamespace(**d))
        index = 1
        for channel in channels:
            print(str(index) + ": " + channel.name)
            index = index + 1

    if command.startswith("send"):
        arg = command.split(" ", 1)[1:]
        arg_joined = "".join(arg)
        message = {
            "content": str(arg_joined)
        }
        print(scopeuser.id, scopeuser)
        if lastcommand == 1:
            resp2 = requests.post("https://discord.com/api/v9/channels/" + scopeuser.id + "/messages", headers=head,
                                  data=message)
        if lastcommand == 2:
            resp2 = requests.post("https://discord.com/api/v9/channels/" + scopeuser.id + "/messages", headers=head,
                                  data=message)
        if lastcommand == 3:
            print("choose channel first!")

        if lastcommand == 4:
            channel_msg_resp = requests.post("https://discord.com/api/v10/channels/" + channelscope.id, headers=head,
                                             data=message)
            print(channel_msg_resp.content)
    if command.startswith("goto") or command.startswith("cd"):
        num = command.split(" ", 1)
        scope = int(num[1])
        if lastcommand == 0:
            print("you have to list something first! try dms, mass_dms or guilds")

        if lastcommand == 1:
            scopeuser = dms[scope - 1]

        if lastcommand == 2:
            scopeuser = dms[scope - 1]

        if lastcommand == 3:
            scopeuser = guilds[scope - 1]
        if lastcommand == 4:
            channelscope_exists = True
            channelscope = channels[scope - 1]
