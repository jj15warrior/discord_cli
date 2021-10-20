import requests
import click
import json
from types import SimpleNamespace
import time
import sys
import subprocess
import os
# 
# https://discord.com/developers/docs/resources/channel#get-reactions
try:
    sessions_file = open("sessions", "r")
except:
    sessions_file = open("sessions", "x")
    sessions_file.close()
    sessions_file = open("sessions", "r")

sessions = sessions_file.read().split("\n")[1:]
token = ""

def list_sessions():
    session_index = 1
    for session in sessions:
        print(str(session_index) + ": " + session.split(" :")[0] + " :" + session.split(" :")[1])
        session_index += 1

using_session = False

if sessions != ['']:
    use_session = input("sessions found. use one of them? [y/n]: ")
    if use_session == 'y':
        list_sessions()
        session_idn = input("session number:")
        token = sessions[int(session_idn)-1].split(" :")[0]
        using_session = True

    if not using_session:
        sessions_file.close()
        mode = input("login with token or with email & pass? [t/l]: ")
        if mode == 't':
            token = input("token: ")

        elif mode == 'l':
            email = str(input("E-mail: "))
            password = str(input("Password: "))
            payload = {
                "email": email,
                "password": password
            }
            r = requests.post('https://discord.com/api/v8/auth/login', json=payload).json()
            if "captcha_key" in r:
                print(
                    "A captcha is requested, the email entered is invalid or has been attempted too many times on connection. Rewrite your information.")
                time.sleep(1)
            elif "errors" in r:
                print("An error has occurred. Rewrite your information.")
            else:
                token = r['token']
            if r["token"] == None:
                print("-----------2FA Authentication-----------")
                code = input("Enter the 2FA authentication code: ")
                mfa_payload = {
                    "code": code,
                    "ticket": r["ticket"]
                }
            r2 = requests.post('https://discord.com/api/v8/auth/mfa/totp', json=mfa_payload).json()
            if "message" in r2:
                print("The 2FA authentication code is incorrect. Rewrite the code.")
                time.sleep(1)
            else:
                token = r2['token']

        save = input("save session? [y/n]: ")
        if save == "y":
            sessions_file = open("sessions", "a")
            sessions_file.write("\n" + token + " :" + input("session name:"))

head = {
    "Authorization": token
}


def analyze_msg(message_to_parse):
    for i in range(len(message_to_parse)):
        if message_to_parse[i] == "<" and message_to_parse[i+1] == "@":
            idOsoby = ""
            for j in range(i, len(message_to_parse)):
                idOsoby += message_to_parse[j]
                if message_to_parse[j] == ">":
                    przed = message_to_parse[:i]
                    po = message_to_parse[i + len(idOsoby):]
                    return [przed, idOsoby[3:-1], po]
    return ["", message_to_parse, ""]

def search_for_emojis(message):
    for i in range(len(message)):
        if message[i] == "<" and message[i+1] == ":":
            emojiTag = ""
            for j in range(i, len(message)):
                emojiTag += message[j]
                if message[j] == ">":
                    przed = message[:i]
                    po = message[i + len(emojiTag):]
                    return przed + ":" + emojiTag[2:-1].split(":")[0].upper() + ":" + po
    return message
                


def parse_uname(mentioned_id):
    mentioned_uname_unparsed = requests.get("https://discord.com/api/users/" + mentioned_id, headers=head)
    mentioned_uname = json.loads(mentioned_uname_unparsed.content, object_hook=lambda d: SimpleNamespace(**d))
    return str(mentioned_uname.username) 


resp = requests.get("http://discord.com/api/users/@me", headers=head)
if resp.status_code != 200:
    print(resp.content)
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

    if command == "guilds" or command == "servers" or command == "sv":
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

    if command == "channels" or command == "ch":
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
            channel_msg_resp = requests.post("https://discord.com/api/channels/" + channelscope.id + "/messages",
                                             headers=head,
                                             data=message)
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

    if command.startswith("history") or command.startswith("hist"):  # Show recent messages
        #   https://discord.com/developers/docs/resources/channel#get-channel-messages

        num = int(command.split(" ", 1)[1])
        if lastcommand == 4:
            messages_unparsed = requests.get("https://discord.com/api/channels/" + channelscope.id + "/messages",
                                             headers=head)
        elif lastcommand == 3:
            print("choose channel first!")
        elif lastcommand == 2:
            messages_unparsed = requests.get("https://discord.com/api/channels/" + scopeuser.id + "/messages",
                                             headers=head)
        elif lastcommand == 1:
            messages_unparsed = requests.get("https://discord.com/api/channels/" + scopeuser.id + "/messages",
                                             headers=head)
        else:
            print("unexpected error!")


        messages = json.loads(messages_unparsed.content, object_hook=lambda d: SimpleNamespace(**d))
        msgindex = 1
        mention_index = 0
        messages_to_print = []

        for msg in messages:
            if msgindex > num:
                break
            # print(str(analyze_msg(msg.content)))
            
            analyzed = analyze_msg(msg.content)
    
            if analyzed[1] == msg.content:  # W wiadomości nie ma wzmianki
                #print(parse_uname(msg.author.id)+": " + msg.content)
                analyzed[1] = search_for_emojis(msg.content)
                messages_to_print.append(parse_uname(msg.author.id)+": " + analyzed[1])
            else:
                #print(parse_uname(msg.author.id)+": " + analyzed[0] + parse_uname(analyzed[1]) + analyzed[2])
                analyzed[0] = search_for_emojis(msg.content)
                analyzed[2] = search_for_emojis(msg.content)
                messages_to_print.append(parse_uname(msg.author.id)+": " + analyzed[0] + parse_uname(analyzed[1]) + analyzed[2])
            
            msgindex += 1
        
        msgindex = 0  # enables printing in reverse
        for msg in reversed(messages_to_print):
            if msgindex > num:
                break
            print(msg)
            msgindex += 1

