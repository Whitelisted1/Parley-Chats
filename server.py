"""

Parley Chats from https://github.com/Parley-Chats

Developed by Whitelisted and HighSecurity

"""



from flask import Flask, request, send_file, abort
from os.path import join, isdir, basename
from os import mkdir, listdir
from datetime import datetime
import hashlib
import uuid
from random import randint
from time import time, sleep
from werkzeug.utils import secure_filename
from PIL import Image
import traceback
import json
# from threading import Thread

# make any changes

"""Required modules:
flask
pyopenssl

Flask==2.0.2
Pillow==9.0.0
Werkzeug==2.0.2
gunicorn==20.1.0
"""
# Add an admin commands thing
# ^ maybe have a seperate page that can only be accessed if they are an admin
    
global loggedin, profanitylist
mafia = None
Detective = None

loggedin = []

directory = __file__[:-len(basename(__file__))] # get file path
storage = directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = join(directory, "uploads")
app.config['MAX_CONTENT_LENGTH'] = 8 * 1000 * 1000
# socketio = SocketIO(app, cors_allowed_origins='*')

open(join(directory, "admins.txt"), "a").close() # if the admins.txt file does not exist, create it
kicked = []
adminusers = ["1234", "highsecurity"]
banip = []
muted = []
numberofmessages = 0
notallowed = ["/", "\\", "~", "`", "<", ">", ",", ".", "'", "\"", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "{", "}", "[", "]", "+" "=", "|", ";", ":", "?", " "]
notallowedusernames = ["admin", "none", "administrator", "mod", "moderator", "default", "nan", "invalid", "false", "true", "server", "computer", "con", "prn", "aux", "nul"]
defaultcolors = ["red", "blue", "default", "orange", "green", "orange", "violet"]
startuptime = time()

f = open(join(directory, "profanity_list.wlist"), encoding="utf-8")
profanitylist = f.read().split("\n") # get profanity list
f.close()

def log(message, log=False):
    now = datetime.now()
    filename = now.date()
    now = f"{now.date()}-{now.hour}_{now.minute}_{now.second}"

    if log: print(f"[{now}] {message}")
    try: f = open(join(directory, "logs", f"{filename}.log"), "a")
    except: f = open(join(directory, "logs", f"{filename}.log"), "w")
    f.write(f"[{now}] {message}\n")
    f.close()

def addnav(file): # add the navigation bar
    user = gettokenuser(request.cookies.get("Token"))
    try:
        startofbody=file.index("<head>")+6 # Length of <body>
        f = open(join(directory, "global", "nav.html"), "r")
        nav = f.read()
        f.close()
        # f = open(join(storage, "admins.txt"))
        # admins = f.read()
        # f.close()
        if str(user).lower() in adminusers:
            nav = nav.replace('<a href="" onclick="switchtheme()"><li>Switch Theme</li></a>', '<a href="" onclick="switchtheme()"><li>Switch Theme</li></a>\n\n<a href="/admin"><li>Admin Menu</li></a>')
        return f"{file[:startofbody]}\n{nav}{file[startofbody:]}"
    except Exception as e:
        log(f"Unable to add nav to a file: {e}", log=True)
        return file


def customhash(text, salt=False):
    hashingsalt = "ac7a76e7290c46548c14036208b2f3667a25d45b64a54ef18b6ce960dd1536b5ddc5395fa5b8404e83cd71a25b372e61c7f753ac94af4daf8ff4616d59e65baeb5b650c67b5a48af8a192f2963851a72c3ce48d114114ec7ab0ecf5f3258081e4ecde1cf7ac7473badb200d71c0852c2dbefcab5e625446b91ea6dc526e322a2890f18b6e54644ada57836fbaa753f5feaa416f4151d43f7ad2e42bfa6a61780d5b688e10095450e8cad13b32bcc69e4cabdddc581d14c45b11bd34b3dba721f99847f9f12604a778503ab3ee219cbb9feb93c5ce74c4d87951c456bc21c70500a692aabf27c4249bc99e87a9803025fbc8479cc2e3e453d8b810326c6aaba454b2b129b75e24327b41095f948941b23f91ee1ae019c4f91805a0af9d9a81e77861968af3cc74697ab7e1ba9205065a6b44cd1c8ad364f7ab3e83f76d03e30823a81e3afde434ba8968b2102fda091464df230d7668340dc93e46231204f1defb8fbac93baba4bb0875d28c91233a9612720b595cc90436eb00d2ec1c3c5eb943e9f20c51fa34a5d91c02a4285362f5771b01905610246bc8fe81c8af56e297a0cb033c9b1be4827986573cde406efdbc64dadb44bb740e085d9dc4271ac5c410ea9358602aa4fceb3ea69d55685d3e59f5801f5b6194ee2b6dd642b3376f0bd111d561f2cb7480992ca84d48ae8e1f0e7acaff0b8ef43f78f6167c35cfb1f762ade308dcb63434093fe31a7d04bf612882d0da84c5846ffa5377a9b209e16c03ad70bb9a8774ea381c3feb14a527709785c9ac2611f4315b60b6576a94c46aed639ee36be85467d84be52f0dee20f2e605f9ed8e0084faaa7dcf581d0943f7a85fc88292c5843268a27919abf01462869fa1d6842944ca5aeb2a7d262155d181e2e8db3715c48df8dfdb271bb6f2390c24e08add7f5417f91a8e6f9c2718d580423d76e0348457cb2b417534684b74f79ed2584379a4df3b1eb9c10270d7023"
    # extra hashing salt in case 'they' don't look at the source code
    if salt == True:
        text = text + hashlib.sha512(hashingsalt.encode("utf-8")).hexdigest()
    for i in range(1250000): # since the hashing algorithm is weak, do it multiple times
        text = hashlib.sha512(f"{text}".encode("utf-8")).hexdigest()
    return text

def getuserinfo(user, info):
    f = open(join(storage, "userinfo", user, "info.txt"), "r")
    settings = f.read().split("\n")
    f.close()
    for setting in settings:
        if setting.split(":")[0] == info:
            return setting.split(":")[1]
    return "None"

def setuserinfo(user, info, value):
    f = open(join(storage, "userinfo", user, "info.txt"), "r")
    contents = f.read().split("\n")
    print(contents)
    linenumber = -1
    for i in range(len(contents)):
        line = contents[i]
        if line != "":
            print(info)
            print(line.split(":")[0])
            if line.split(":")[0] == info:
                linenumber = i
                break
    f.close()
    
    if linenumber != -1:
        f = open(join(storage, "userinfo", user, "info.txt"), "w")
        for i in range(len(contents)):
            line = contents[i]
            if i == linenumber:
                f.write(f"\n{info}:{value}")
            elif line != "":
                f.write(f"\n{line}")
        f.close()
    else:
        f = open(join(storage, "userinfo", user, "info.txt"), "a")
        f.write(f"\n{info}:{value}")
        f.close()

def getusernames(file="users.txt", lower=False):
    if file[0] == "/" or file[0] == "\\":
        file = file[1:]
    try:
        f = open(join(storage, file), "r")
        users = f.read().split("\n")
        f.close()
    except FileNotFoundError:
        return [], [], []
    usernames = []
    passwords = []
    salts = []
    for user in users:
        if user != "" and user != " ":
            dict = json.loads(user)
            if lower:
                usernames.append(dict["username"].lower())
            else:
                usernames.append(dict["username"])
            passwords.append(dict["password"])
            salts.append(dict["salt"])
    return usernames, passwords, salts


def gettokenuser(usertoken):
    for token in loggedin:
        token = token.split(":")
        if token[1] == usertoken:
            username = token[0]
            return username
        
    return None

        
def getcontents(file, addingnav=False, theme=False):
    f = open(join(directory, file), "r")
    contents = f.read()
    f.close()
    if addingnav == True:
        contents = addnav(contents)

    if theme=="dark":
        f = open(join(directory, "global", "darkmode.css"), "r")
        darkmodecontents = f.read()
        darkmodecontents = f"<style>{darkmodecontents}</style>"
        f.close()
        try:
            startofbody=contents.index("<head>")+6 # Length of <body>
            contents = f"{contents[:startofbody]}\n{darkmodecontents}{contents[startofbody:]}".replace('<a href="/account"><img src="/images/default_profile_picture.png" width=20></a>', '<a href="/account"><img src="/images/darkmode_default_profile_picture.png" width=20></a>')
        except Exception as e:
            log(f"Unable to add darkmode to a file: {e}", log=True)        
    else:
        f = open(join(directory, "global", "lightmode.css"), "r")
        lightmodecontents = f.read()
        lightmodecontents = f"<style>{lightmodecontents}</style>"
        f.close()
        try:
            startofbody=contents.index("<head>")+6 # Length of <body>
            contents = f"{contents[:startofbody]}\n{lightmodecontents}{contents[startofbody:]}"
        except:
            pass
            
    return contents
def getbytes(file):
    f = open(join(directory, file), "br")
    contents = f.read()
    f.close()
    return contents

def archivechannels():
    while True:
        sleep(60)
        
        for file in listdir(join(directory, "chat")):
            if isdir(file):
                try:
                    f = open(join(directory, "chat", file, "chat.txt"), "r")
                    lasttime = f.read().split("\n")[-1].split(":")[0]
                    f.close()
                    
                    if float(time()-int(lasttime)) > 86400:
                        f = open(join(directory, "chat", file, "config.txt"), "r")
                        config = f.read().split("\n")
                        f.close()

                        f = open((join(directory, "chat", file, "config.txt"), "w"))
                        for i in range(len(config)):
                            if i == len(config)-1:
                                f.write("yes")
                            f.write(f"{i}\n")
                        f.close()
                except: pass
                


@app.route("/icon/<icon>")
def geticon(icon):
    return getbytes(join("icons", icon))
@app.route("/favicon.ico")
def getmainicon():
    return getbytes(join("icons", "favicon.ico"))


@app.route("/uploads/<roomuuid>/images/<image>")
def getcustomimage(image, roomuuid):
    image = image.replace("/", "\\")
    user = gettokenuser(request.cookies.get("Token"))
    if roomuuid == "main": config = ["Main chat room", "yes", "", '000000000', "0"]
    else:
        f = open(join(directory, "chat", roomuuid, "config.txt"), "r")
        config = f.read().split("\n")
        f.close()
    if user in config[2].split(",") or config[1] == "yes":
        if user != None:
            return getbytes(join("uploads", roomuuid, "images", f"small-{image}"))
        else:
            return errormessage("/index.html", "You need to sign in to continue")
    return "No permissions"

@app.route("/uploads/<roomuuid>/images/<image>/download")
def downloadcustomimage(image, roomuuid):
    image = image.replace("/", "\\")
    user = gettokenuser(request.cookies.get("Token"))
    if roomuuid == "main": config = ["Main chat room", "yes", "", '000000000', "0"]
    else:
        f = open(join(directory, "chat", roomuuid, "config.txt"), "r")
        config = f.read().split("\n")
        f.close()
    if user in config[2].split(",") or config[1] == "yes":
        if user != None:
            return send_file(join(directory, "uploads", roomuuid, "images", image))
        else:
            return errormessage("/index.html", "You need to sign in to continue")
    return "No permissions"

@app.route("/uploads/<roomuuid>/<file>")
def getcustomfile(file, roomuuid):
    file = file.replace("/", "\\")
    user = gettokenuser(request.cookies.get("Token"))
    if roomuuid == "main":
        config = ["Main chat room", "yes", "", '000000000', "0"]
    else:
        f = open(join(directory, "chat", roomuuid, "config.txt"), "r")
        config = f.read().split("\n")
        f.close()
    if user in config[2].split(",") or config[1] == "yes":
        if user != None:
            return getbytes(join("uploads", roomuuid, file))
        else:
            return errormessage("/index.html", "You need to sign in to continue")
    return "No permissions"

@app.route("/images/<image>")
def images(image):
    return getbytes(f"images/{image}")

@app.route("/jquery")
def getjquery():
    return getcontents("jquery-3.6.0.min.js")


def errormessage(url, message, othercode=""):
    message = message.replace(" ", "+")
    return f"<script>{othercode}window.location=\"{url}?fail={message}\";</script>"

    
class api:
    # @app.route("/api/changepassword", methods=["POST"])
    # def changepassword():
    #     usernames, passwords, salts = getusernames()
    #     username = gettokenuser(request.cookies.get("Token"))
    #     index = usernames.index(username)

    #     oldpass = request.form["currentpass"]
    #     newpass = request.form["newpass"]

    #     if customhash(oldpass + salts[index]) == passwords[index]:
    #         newpasshash = customhash(newpass + salts[index])
    #         f = open(join(storage, "users.txt"), "w")
    #         for i in range(len(usernames)):
    #             if i == index:
    #                 f.write(f'\n{{"username": "{username}", "password": "{newpasshash}", "salt": "{salts[index]}"}}')
    #             else: f.write(f'\n{{"username": "{usernames[i]}", "password": "{passwords[i]}", "salt": "{salts[i]}"}}')
    #         return errormessage("/index.html", "Successfully changed password")
    #     else:
    #         return errormessage("/account", "Password is incorrect")
        
    @app.route("/api/changecolor", methods=["POST"])
    def changecolor():
        color = request.form["color"].lower()
        user = gettokenuser(request.cookies.get("Token"))
        f = open(join(storage, "donators.txt"))
        donators = f.read().split("\n")
        f.close()
        
        if user not in donators:
            if color not in defaultcolors:
                return f"You are not a donator<br>Unable to set your color to {color}"
        # print(color)
        setuserinfo(user, "chatcolor", color)
        return f"Changed color to <b style=\"color: {color}\">{color}</b>"


    @app.route("/api/sendmessage/<roomuuid>", methods=["POST"])
    def sendmessageuuid(roomuuid):
        global numberofmessages
        user = gettokenuser(request.cookies.get("Token"))
        if user == None: return "No username"
        # adminusers, temp, temp = getusernames("admins.txt")
        color = getuserinfo(user, "chatcolor")
        if user.lower() in adminusers and request.cookies.get("chatcolor") == "gradient":
            color = "gradient"
        elif color == None:
            color = 'default'

        if color not in defaultcolors:
            f = open(join(storage, "donators.txt"), "r")
            donators = f.read().split("\n")
            f.close()
            if user not in donators:
                color = "default"

        message = request.form['message'].replace("[", "-").replace("]", "-").replace("<", "-").replace(">", "-").replace("%", "-").replace(":", "-").strip()
        if message.replace(" ", "") == "":
            return "No message"
        
        if len(message) > 200:
            message = message[:200]
        if message[0] == "/":
            if user.lower() in adminusers:
                success = False
                command = message[1:]
                if command.startswith("kickuser "):
                    arg = command[len("kickuser "):]
                    success = admin.kickuser(user)
                    if success:
                        log(f"{user} kicked {arg}", log=True)

                elif command.startswith("banuer "):
                    arg = command[len("banuser "):]
                    success == admin.banuser(arg)
                    if success:
                        log(f"{user} banned {arg}", log=True)

                elif command.startswith("banip "):
                    arg = command[len("banip "):]
                    if "." in arg:
                        success = admin.banip(ip=arg)
                        if success:
                            log(f"{user} banned the ip {arg}")
                    else:
                        success = admin.banip(user=arg)
                        if success:
                            log(f"{user} banned the ip {arg}")

                elif command.startswith("mute "):
                    arg = command[len("mute "):].lower()
                    users, temp, temp = getusernames(lower=True)
                    if arg in users:
                        muted.append(arg)
                        if roomuuid == "main":
                            f = open(join(directory, "chat.txt"), "a")
                        else:
                            f = open(join(directory, "chat", roomuuid, "chat.txt"), "a")
                        f.write(f"\n{arg} was muted")
                        f.close()
                        success = True
                    else:
                        print(arg, "does not exist")
                        return "False"
                
                elif command.startswith("unmute "):
                    try:
                        arg = command[len("unmute "):].lower()
                        users, temp, temp = getusernames()
                        if arg in muted:
                            muted.remove(arg)
                            if roomuuid == "main":
                                f = open(join(directory, "chat.txt"), "a")
                            else:
                                f = open(join(directory, "chat", roomuuid, "chat.txt"), "a")
                            f.write(f"\n{arg} was unmuted")
                            f.close()
                            success = True
                        else:
                            return "False"
                    except:
                        print(traceback.format_exc())

                elif command.startswith("unban "):
                    arg = command[len("unban "):]
                    success = admin.banip(user=arg)
                    if success:
                        log(f"{user} unbanned {arg}", log=True)
                
                elif command == "clear":
                    if roomuuid == "main":
                        f = open(join(directory, "chat.txt"), "w")
                        f.write(f"Chat cleared by {user}")
                        f.close()
                    else:
                        f = open(join(directory, "chat", roomuuid, "config.txt"), "r")
                        config = f.read().split()
                        f.close()
                        f = open(join(directory, "chat", roomuuid, "chat.txt"), "w")
                        if config[1] == "no":
                            people = ""
                            for i in range(len(config[2].split(","))):
                                if i != 0:
                                    people += f", {config[2].split(',')[i]}"
                            f.write(f"{config[2].split(',')[0]} created a private room with {people[2:]}.\nYou can invite more people with the room code: {config[3]}\n\nThe room chat was cleared by {user}")
                        else:
                            f.write(f"{config[2].split(',')[0]} created a public room.\nThe chat room was cleared by {user}")
                        f.close()

                elif command.startswith("purge" ):
                    arg = command[len("purge "):].lower().strip()
                    try:
                        arg = int(arg)
                        if roomuuid == "main":
                            f = open(join(directory, "chat.txt"), "r")
                        else:
                            f = open(join(directory, "chat", roomuuid, "chat.txt"), "r")
                        content = f.read().split("\n")
                        f.close()

                        if roomuuid == "main":
                            f = open(join(directory, "chat.txt"), "w")
                        else:
                            f = open(join(directory, "chat", roomuuid, "chat.txt"), "w")

                        for i in range(len(content[:-arg])):
                            if i == 0:
                                f.write(f"{content[i]}")
                            else:
                                f.write(f"\n{content[i]}")
                        f.close()
                        success = True
                    except:
                        print(traceback.format_exc())
                        success = False
                
                elif command.startswith("deop "):
                    arg = command[len("deop "):].lower().strip()
                    if user == "1234":
                        adminusers.remove(arg)
                        success = True
                    else:
                        success = False
                # elif command.startswith("sudo "):
                #     args = command[len("sudo "):].lower().strip().split()
                #     if roomuuid == "main":
                #         f = open(join(directory, "chat.txt"), "a")
                #     else:
                #         f = open(join(directory, "chat", roomuuid, "chat.txt"), "a")
                    
                #     message = ""
                #     for item in args[1:]:
                #         message += f" {item}"
                    
                    
                #     f.write(f"")
                #     f.close()


                if success:
                    log(f"{user} executed the command: '{message}'", log=True)
                    return "Command successful"
                else:
                    log(f"{user} tried to execute an invalid command: '{message}'", log=True)
                    return "Command error"
            
            return "User is not an admin"

        else:
            if user.lower() in muted:
                return "You are muted."
            if roomuuid == "main":
                config = ["Main chat room", "yes", "", '000000000', "0"]
            else:
                f = open(join(directory, "chat", roomuuid, "config.txt"), "r")
                config = f.read().split("\n")
                f.close()
            try:
                temp = message.encode("ascii")
            except:
                if roomuuid == "main":
                    f = open(join(directory, "chat.txt"), "a")
                else:
                    f = open(join(directory, "chat", roomuuid, "chat.txt"), "a")
                f.write(f"\n{user} tried to send a message, but it contained 'weird' text")
                f.close()
                return "Invalid character"
            if user in config[2].split(",") or config[1] == "yes":
                numberofmessages += 1
                if roomuuid == "main": f = open(join(directory, "chat.txt"), "r")
                else: f = open(join(directory, "chat", roomuuid, "chat.txt"), "r")
                lines = f.read().split("\n")
                lastline = lines[-1]
                f.close()
                stackmessages = True
                try: temp = lastline.split("::")[1]
                except: stackmessages = False
                try:
                    if stackmessages == True:
                        splitmes = lastline.split("::")[1].split("[")[1].split("]")

                        lastlineuser = splitmes[0]
                        lastlinemessage = splitmes[1].split("</pre>")[0].split("onclick=\"copytext(this)\">")[1]
                        # print(lastlinemessage.strip())
                        # print(message.strip())
                        if lastlineuser == user and lastlinemessage.strip() == message.strip():
                        # if f'[{user}]: {message}' == lastline[0].split("::")[1].strip():
                            if roomuuid == "main": f = open(join(directory, "chat.txt"), "w")
                            else: f = open(join(directory, "chat", roomuuid, "chat.txt"), "w")
                            for line in lines[:-1]:
                                f.write(f"{line}\n")
                            try:
                                times = int(splitmes[1].split("</pre>")[1].strip().split("<")[1].split(">")[0])
                            except:
                                times = 1
                            if times != 1:
                                f.write(f'{time()}::{lastline.strip().split("::")[1][:-(3+len(str(times)))]} <{int(times)+1}>')
                            else:
                                f.write(f'{time()}::{lastline.strip().split("::")[1]} <{int(times)+1}>')
                            f.close()
                            return "Sent message."
                        else:
                            stackmessages = False
                except:
                    stackmessages = False
                
                if stackmessages == False:
                    # profanitycheck = True
                    # for item in profanitylist:
                    #     try:
                    #         index = message.lower().index(item.lower())
                    #         message = message[:index] + "*"*len(item) + message[index+len(item):]
                    #     except ValueError:
                    #         pass

                    splitmessage = message.split()
                    for i in range(len(splitmessage)):
                        if splitmessage[i] in profanitylist:
                            print(True)
                            splitmessage[i] = "*"*len(splitmessage[i])
                    message = ""
                    for i in range(len(splitmessage)):
                        if i == 0:
                            message = splitmessage[i]
                        else:
                            message += f" {splitmessage[i]}"
                            
                        
                        # if item in message:
                        #     log(f"{user} tried to send a message, but it was filtered by the profanity check", log=True)
                    if roomuuid == "main":
                        f = open(join(storage, "chat.txt"), "a")
                    else:
                        f = open(join(storage, "chat", roomuuid, "chat.txt"), "a")
                    
                    f.write(f"\n{time()}::")
                    
                    if user.lower() in adminusers:
                        f.write("&#128081;")

                    f.write(f"<a class=\"user\" href=\"/users/{user}\"")

                    if color == "gradient":
                        f.write(" id=\"admincolor")
                    else:
                        if color != "default":
                            f.write(f' style="color:{color}')  
                        
                    f.write(f"\">[{user}]</a>: <pre class=\"chattext\" onclick=\"copytext(this)\">{message}</pre>")
                    f.close()
                    return "Sent message." 
                    # else:
                    #     return "Message is not allowed."
                else: return "Sent message."

            else: log(f"{user} is trying to send a message to {roomuuid}!", log=True); return "You don't have access to this chat room"
    
    @app.route("/api/sendfile/<roomuuid>", methods=["POST", "GET"])
    def sendfile(roomuuid):
        user = gettokenuser(request.cookies.get("Token"))
        if user.lower() in muted:
            return "You are muted"
        isfile=True
        try: file = request.files['file']
        except: return "An error occured."
            
        
        if file.content_length > app.config['MAX_CONTENT_LENGTH']:
            f = open(join(directory, "chat", roomuuid, "chat.txt"), "a")
            f.write(f"\n{user} tried to send a file, but it was bigger than 8mb")
            f.close()
            return "File is too large. Maximum upload size is 8mb"

        if file.filename == '':
            isfile=False
        if isfile:
            extension = secure_filename(file.filename).split(".")[-1]
            filename = uuid.uuid4().hex + uuid.uuid4().hex + uuid.uuid4().hex + uuid.uuid4().hex
            pictures = ["jpeg", "jpg", "png", "gif", "tiff", "webp", "bmp"]
            out = app.config["UPLOAD_FOLDER"]# replace("\\", "/")
            if not isdir(join(directory, "uploads", roomuuid)): 
                mkdir(join(out, roomuuid))
                mkdir(join(out, roomuuid, "images"))

            for picextension in pictures:
                if extension.lower() == picextension:
                    # try: open(f"{out}/{roomuuid}/images/{filename}.{extension}", "x").close(); open(f'{out}/{roomuuid}/images/small-{filename}.{extension}', "x").close()
                    # except Exception as e: print(e)
                    file.save(f"{out}/{roomuuid}/images/{filename}.{extension}")
                    
                    img = Image.open(join(out, roomuuid, "images", f"{filename}.{extension}"))
                    img.thumbnail((300, 200))
                    img.save(f'{out}/{roomuuid}/images/small-{filename}.{extension}', quality=80)

                    if roomuuid == "main": f = open(join(directory, "chat.txt"), "a")
                    else: f = open(join(directory, "chat", roomuuid, "chat.txt"), "a")
                    f.write(f"\n\n<Image:<a class=\"user\" href=\"/users/{user}\">[{user}]</a>:/uploads/{roomuuid}/images/{filename}.{extension}")
                    f.close()
                    return "Uploaded image."

            file.save(f"{out}/{roomuuid}/{filename}.{extension}")
            if roomuuid == "main": f = open(join(directory, "chat.txt"), "a")
            else: f = open(join(directory, "chat", roomuuid, "chat.txt"), "a")
            f.write(f"\n\n<File:<a class=\"user\" href=\"/users/{user}\">[{user}]</a>:{secure_filename(file.filename).replace('<', '').replace('>', '').replace(':', '')}:/uploads/{roomuuid}/{filename}.{extension}")
            f.close()
            return "Uploaded file."
        else:
            return "No file"

    @app.route("/api/chat")
    def getchat():
        user = gettokenuser(request.cookies.get("Token"))
        users, temp, temp = getusernames()
        lengthoffile = request.args.get("length")
        timestamp = float(request.args.get("timestamp"))
        # print(timestamp)
        if user in users:
            f = open(join(storage, "chat.txt"))
            filecontents = f.read()
            f.close()

            splitfilecontents = filecontents.split("\n")
            if len(splitfilecontents) > 100:
                splitfilecontents = splitfilecontents[-100:]
                contents = ""
                for i in range(len(splitfilecontents)):
                    if i == 0:
                        contents = splitfilecontents[i]
                    else:
                        contents += f"\n{splitfilecontents[i]}"
            else:
                contents = filecontents

            # lines = []
            if len(contents) != int(lengthoffile):
                # for line in contents.split("\n"):
            #         try:
            #             timesent = float(line.split("::")[0])
            #             if timesent > timestamp:
            #                 lines.append(line)
            #         except:
            #             pass
            #             # print(traceback.format_exc())

            #     newlines = ""
            #     for i in range(len(lines)):
            #         if i == 0:
            #             newlines += lines[i]
            #         else:
            #             newlines += f"\n{lines[i]}"
                return contents+f"%{time()-2}%"
            else:
                return f"0:{time()-2}"
        else:
            # if lengthoffile == "75": # Length of error message
            #     return f"0:{time()-2}"
            return "<b style=\"text-align: center;\">You have to sign in to view this channel!<b>"

    @app.route("/api/chat/<roomuuid>")
    def getchatuuid(roomuuid):
        user = gettokenuser(request.cookies.get("Token"))
        users, temp, temp = getusernames()
        lengthoffile = request.args.get("length")
        timestamp = float(request.args.get("timestamp"))
        # print(timestamp)
        if user in users:
            f = open(join(storage, "chat", roomuuid, "config.txt"), "r")
            config = f.read().split("\n")
            f.close()
            if user in config[2].split(",") or config[1] == "yes":
                f = open(join(storage, "chat", roomuuid, "chat.txt"))
                contents = f.read()
                f.close()

                if len(contents) != int(lengthoffile):
                    return contents+f"%{time()-2}%"
                else:
                    # if lengthoffile == "67": # Length of error message
                    #     return f"0:{time()-2}"
                    return f"0:{time()-2}"
            else:
                return "<b style=\"text-align: center;\">You don't have access to this room!<b>"
        else:
            # if lengthoffile == "69": # Length of error message
            #     return f"0:{time()-2}"
            return "<b style=\"text-align: center;\">You don't have access to this room!<b>"

    @app.route("/api/checkuser", methods=['GET', 'POST'])
    def checkuserexists():
        username = gettokenuser(request.cookies.get("Token"))
        users, temp, temp = getusernames(lower=True)
        user = request.form['usersubmit'].lower()
        if username.lower() in users:
            if user in users:
                if username.lower() != user:
                    return "True"
                else: return "You can't add yourself"
        else:
            return "Not logged in"
        print("returned false")
        return "False"
    
    @app.route("/api/createroom/check", methods=['GET', 'POST'])
    def checkcreateroom():
        usercreating = gettokenuser(request.cookies.get("Token"))
        users, temp, temp = getusernames(lower=True)

        if usercreating == None:
            return errormessage("/index.html", "You are not signed in. Please sign in to continue")
        if usercreating.lower() in users:
            roomname = request.form['roomname']
            if roomname.replace(" ", "") == "": return errormessage("/home/createroom", "You cannot leave the roomname field blank!")
            ispublic = request.form['ispublic']
            usersinchat = request.form['usersinchat'].split(";")
            for word in roomname.split():
                if word in profanitylist:
            # for item in profanitylist:
            #     if item in roomname:
                    return errormessage("/home/createroom", "Roomname was flagged by profanity list")
            if len(usersinchat) == 1 and ispublic == "no":
                # print(usersinchat)
                return errormessage("/home/createroom", "You need at least 1 other user in order to make a group chat")

            if roomname.replace(" ", "") != "":
                for symbol in notallowed:
                    if symbol != " " or symbol != "." or symbol != "'":
                        if symbol in roomname: return errormessage("/home/createroom", "Illegal symbol is in the roomname")

            for user in usersinchat:
                if user != "":
                    if user.lower() not in users:
                        return errormessage("/home/createroom", "A selected user is not available.")

            run = True
            while run:
                run = False
                roomuuid = uuid.uuid4().hex + uuid.uuid4().hex + uuid.uuid4().hex + uuid.uuid4().hex
                for file in listdir(join(directory, "chat")):
                    if roomuuid == file:
                        run = True

            mkdir(join(directory, "chat", roomuuid))

            f = open(join(directory, "chat", roomuuid, "config.txt"), "w")
            msg = f'{roomname}\n{ispublic}\n{usercreating},'
            for user in usersinchat:
                if user != "":
                    msg += f"{user},"
            msg = msg[:-1]
            code = ""
            for i in range(9):
                code = code + str(randint(0, 9))
            msg += f"\n{code}\n{time()}\nno"
            f.write(msg)
            f.close()

            f = open(join(directory, "chat", roomuuid, "chat.txt"), "w")
            if ispublic == "no":
                msg = f"'{usercreating}' created a room with"
                for user in usersinchat:
                    if user != "":
                        msg += f" '{user}',"
                msg = msg[:-1]
                msg += f"\nYou can invite more people with the join code '{code}'"
            else:
                msg = f"'{usercreating}' created a public room called '{roomname}'\n"
            f.write(msg)
            f.close()   

            f = open(join(directory, "chat", "template.html"), "r")
            template = f.read()
            f.close()
            f = open(join(directory, "chat", "main.js"), "r") 
            templatejs = f.read()
            f.close()

            template = template.replace("{roomuuid}", roomuuid).replace("<title>", f"<title>{roomname} | Parley").replace("{roomcode}", code)
            templatejs = templatejs.replace("{roomuuid}", roomuuid)

            f = open(join(directory, "chat", roomuuid, "index.html"), "w") 
            f.write(template)
            f.close()

            f = open(join(directory, "chat", roomuuid, "main.js"), "w")
            f.write(templatejs)
            f.close()


            return f"<script>window.location=\"/home/{roomuuid}\"</script>"
        else:
            return errormessage("/index.html", "You are not signed in. Please sign in to continue")

    @app.route("/api/joinroom/check", methods=["GET", "POST"])
    def checkjoinroom():
        user = gettokenuser(request.cookies.get("Token"))
        users, temp, temp = getusernames()
        if user in users:
            pin = request.form['pin']
            if pin == "000000000":
                return f"<script>window.location=\"/home\"</script>"
            try:    
                int(pin)
                for file in listdir(join(directory, "chat")):
                    if isdir(join(directory, "chat", file)):
                        # print(file)
                        f = open(join(directory, "chat", file, "config.txt"), "r")
                        config = f.read().split("\n")
                        filepin = config[3]
                        usersinchat = config[2].split(",")
                        f.close()
                        if filepin == pin:
                            if user not in usersinchat:
                                f = open(join(directory, "chat", file, "config.txt"), "w")
                                config[2] = config[2] + f",{user}"
                                for line in config:
                                    f.write(f'{line}\n')
                                f.close()
                                f = open(join(directory, "chat", file, "chat.txt"), "a")
                                f.write(f"\n{user} joined the room with the code '{pin}'")
                                f.close()
                                return f"<script>window.location=\"/home/{file}\"</script>"
                            else:
                                return errormessage("/home/joinroom", "You are aready in this room!")
                        # also make the people thing work, get users from config file and then put them in thatbox
            except: return errormessage("/home/joinroom", "An error occured.")

            return "True"
        else:
            return errormessage("/index.html", "You are not signed in. Please sign into continue")
    
    @app.route("/api/suggestions/send", methods=['GET', 'POST'])
    def sendsuggestion():
        username = gettokenuser(request.cookies.get("Token"))
        suggestion = request.form['suggestion']

        if username == None: return errormessage("/index.html", "You must be signed in to make a suggestion")
        if suggestion.strip() == "": return "No content in suggestion."

        f = open(join(directory, "suggestions.txt"), "a")
        f.write(f"[{username}]: {suggestion}\n")
        f.close()

        return "Sent suggestion! Thank you!"

class admin:
    @app.route("/admin")
    def adminmain():
        user = gettokenuser(request.cookies.get("Token"))
        # f = open(join(storage, "admins.txt"))
        # admins = f.read().split("\n")
        # f.close()
        if str(user).lower() in adminusers:
            return getcontents(join(storage, "user", "admin.html"), addingnav=True, theme=request.cookies.get("theme")).replace("{numberofmessages}", str(numberofmessages)).replace("{startup}", str(startuptime))
        else:
            return abort(404)
    @app.route("/admin/main.js")
    def adminjs():
        user = gettokenuser(request.cookies.get("Token"))
        # f = open(join(storage, "admins.txt"))
        # admins = f.read().split("\n")
        # f.close()
        if str(user).lower() in adminusers:
            return getcontents(join(storage, "user", "admin.js"))
        else:
            return abort(404)
    def kickuser(user):
        kicked.append(user)

    def banuser(user):
        f = open("banned.txt", "a")
        f.write(f"\n{user}")
        f.close()

    def banip(user=None, ip=None):
        if user != None:
            banip.append(user)
        elif ip != None:
            f = open("bannedips.txt", "a")
            f.write(f"\n{ip}")
            f.close()
        else: return "No input"

    def unban(user=None, ip=None):
        if user != None:
            f = open("banned.txt", "r")
            users = f.read().split()
            f.close()
            try:
                users.remove(user)
                f = open("banned.txt", "w")
                for user in users:
                    f.write(f"{user}\n")
            except: return "User is not banned"
        elif ip != None:
            f = open("bannedips.txt", "r")
            ips = f.read().split()
            f.close()
            try:
                ips.remove(ip)
                f = open("bannedips.txt", "w")
                for ip in ips:
                    f.write(f'{ip}\n')
                f.close()
            except: return "Ip is not banned"

            
        else: return "No input"

class errorpages:
    @app.errorhandler(404)
    def pagenotfound(e):
        return getcontents('errorpages/404.html'), 404
    @app.errorhandler(410)
    def gone(e):
        return getcontents("errorpages/notavailable.html"), 410
    @app.errorhandler(500)
    def servererror(e):
        user = gettokenuser(request.cookies.get("Token"))
        if user == None:
            user = ""
        contents = getcontents("errorpages/servererror.html")
        if user.lower() in adminusers:
            contents = contents.replace('<pre style="display: none;"></pre>',f'<br><br><pre style="background-color: rgb(192, 192, 192); border: 10px solid gray; box-sizing: auto; padding: 50px; white-space:pre-wrap; border-radius: 1.3em;">{traceback.format_exc()}</pre>')

        return contents, 500 # Change to a code that administrators can view if user is not an admin

class account:
    @app.route("/account")
    def account():
        user = gettokenuser(request.cookies.get("Token"))
        users, temp, temp = getusernames()
        if user == None or user not in users: return errormessage("/index.html", "You are not logged in. Please log in to continue.")
        page = getcontents(join("user", "profile.html"), True, request.cookies.get("theme")).replace("{user}", user)
        return page

    @app.route("/users/<user>")
    def getuser(user):
        # return user
        return getcontents(join("user", "userpagetemplate.html"), addingnav=True, theme=request.cookies.get("theme")).replace("{user}", user).replace("{usercolor}", getuserinfo(user, "chatcolor")).replace("{timestamp}", getuserinfo(user, "accountcreation"))
    
    @app.route("/account/changecolor")
    def getchangecolor():
        user = gettokenuser(request.cookies.get("Token"))
        contents = getcontents(join("user", "changecolor.html"), True, request.cookies.get("theme"))
        if user in getcontents(join(storage, "donators.txt")).split("\n"):
            contents = contents.replace("{selectbox}", '<input type="color" name="color" id="colorselect"><script>donated=1</script>')
        else:
            contents = contents.replace('{selectbox}', '''<select name="color" id="colorselect" style="width: 200px; height: 100px; font-size: 50px;">
            <option id="cdefault">Default</option>
            <option id="cred">Red</option>
            <option id="corange">Orange</option>
            <option id="cblue">Blue</option>
            <option id="cgreen">Green</option>
            <option id="cviolet">Violet</option>
        </select><script>donated=0</script>''')
        return contents

class mainpage:
    @app.route("/")
    def home():
        if request.cookies.get("TOS") == "0" or request.cookies.get("TOS") == None:
            return "<script>window.location=\"/TOS\"</script>"
        if request.cookies.get("updatetime") != str(startuptime): # Change once I get to keep user data
            return "<script>window.location=\"/newupdates\"</script>"
        return getcontents("index.html", True, request.cookies.get("theme"))
    @app.route("/index.html")
    def redirecthome():
        return mainpage.home()
    @app.route("/main.js")
    def getmainjs():
        return getcontents("main.js", True)
    @app.route("/TOS")
    def gettos():
        return getcontents("TOS.html", True, request.cookies.get("theme"))
    @app.route("/aboutus")
    def aboutus():
        return getcontents("aboutus.html", True, request.cookies.get("theme"))
    @app.route("/suggestions")
    def suggestions():
        return getcontents(join("user", "suggest.html"), True, request.cookies.get("theme"))
    @app.route("/newupdates")
    def newupdates():
        return getcontents("newupdates.html", True, request.cookies.get("theme")).replace("{updatetime}", str(startuptime))

class home:
    @app.route("/home/main.js")
    def homejs():
        return getcontents("home/main.js")
    @app.route("/home")
    def loggedin():
        token = request.cookies.get("Token")
        # print(token)
        username = gettokenuser(token)
        if username != None:
            return getcontents("home/index.html", True, request.cookies.get("theme")) + f"<script>document.cookie=\"username={username}; path=/\"</script>"
        else:
            return errormessage("/index.html", "You are not signed in. Please sign in to continue")

    @app.route("/home/createroom")
    def creatroom():
        return getcontents("home/create_room/index.html", True, request.cookies.get("theme"))

    @app.route("/home/createroom/main.js")
    def createroomjs():
        return getcontents("home/create_room/main.js")
    
    @app.route("/home/joinroom")
    def joinroom():
        return getcontents("home/join_room/index.html", True, request.cookies.get("theme"))
    
    @app.route("/home/joinroom/<roomcode>")
    def joinroomlink(roomcode):
        user = gettokenuser(request.cookies.get("Token"))
        users, temp, temp = getusernames()
        if user in users:
            pin = roomcode
            if pin == "000000000":
                return f"<script>window.location=\"/home\"</script>"
            try:    
                int(pin)
                for file in listdir(join(directory, "chat")):
                    if isdir(join(directory, "chat", file)):
                        # print(file)
                        f = open(join(directory, "chat", file, "config.txt"), "r")
                        config = f.read().split("\n")
                        filepin = config[3]
                        usersinchat = config[2].split(",")
                        f.close()
                        if filepin == pin:
                            if user not in usersinchat:
                                f = open(join(directory, "chat", file, "config.txt"), "w")
                                config[2] = config[2] + f",{user}"
                                for line in config:
                                    f.write(f'{line}\n')
                                f.close()
                                f = open(join(directory, "chat", file, "chat.txt"), "a")
                                f.write(f"\n{user} joined the room with the code '{pin}'")
                                f.close()
                                return f"<script>window.location=\"/home/{file}\"</script>"
                            else:
                                return errormessage("/home/joinroom", "You are aready in this room!")
                        # also make the people thing work, get users from config file and then put them in thatbox
            except: return errormessage("/home/joinroom", "An error occured.")

            return "True"
        else:
            return errormessage("/index.html", "You are not signed in. Please sign into continue")
    

    @app.route("/home/<roomuuid>/main.js")
    def roomjs(roomuuid):
        return getcontents(join("chat", roomuuid, "main.js"))

    @app.route("/home/<roomuuid>")
    def roommain(roomuuid):
        user = gettokenuser(request.cookies.get("Token"))
        f = open(join(directory, "chat", roomuuid, "config.txt"), "r")
        config = f.read().split("\n")
        f.close()
        if user in config[2].split(",") or config[1] == "yes":
            if user != None:
                return getcontents(join("chat", roomuuid, "index.html"), True, request.cookies.get("theme"))
            else:
                return errormessage("/index.html", "You are not signed in. Please sign in to continue")
        else:
            log(f"{user} tried to visit {roomuuid}, but doesn't have access", log=True)
            return "You don't have access to this chat room"
    
    @app.route("/home/existingrooms")
    def existingrooms():
        seconds_in_day = 60 * 60 * 24
        seconds_in_hour = 60 * 60
        seconds_in_minute = 60
        user = gettokenuser(request.cookies.get("Token"))
        if user == None: return errormessage("/index.html", "<b style=\"text-align: center;\">You must be signed in to continue</b>")
        userin = []

        before = getcontents("home/join_room/existing.html", True, request.cookies.get("theme"))
        
        for file in listdir(join(directory, "chat")):
            if isdir(join(directory, "chat", file)):
                f = open(join(directory, "chat", file, "config.txt"))
                config = f.read().split("\n")
                
                f.close()
                if config[1] == "no":
                    if user in config[2].split(","):
                        userin.append(file)

                        seconds = int(time()-float(config[4]))
                        days = seconds // seconds_in_day
                        hours = (seconds - (days * seconds_in_day)) // seconds_in_hour
                        minutes = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour)) // seconds_in_minute
                        # seconds = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour) - (minutes * seconds_in_minute))

                        template = f'<a href="/home/{file}" style="text-decoration: none; color: inherit"><pre id="chat" class="chat" style="width: 400px; height: 175px; border: 10px solid rgb(73, 73, 73); padding: 10px; overflow: auto; white-space:pre-wrap; display: inline-block; vertical-align: top;"><h2>{config[0]}</h2><h3>{config[2]}</h3><h4>Created {days} day(s), {hours} hour(s) and {minutes} minute(s)  ago.</h4></pre></a>'

                        before = before.replace("<!-- {templatehere} -->", f"<!-- {{templatehere}} -->\n{template}")
        
        return before

    @app.route("/home/existingrooms/public")
    def existingpublic():
        seconds_in_day = 60 * 60 * 24
        seconds_in_hour = 60 * 60
        seconds_in_minute = 60
        before = getcontents("home/join_room/existing.html", True, request.cookies.get("theme"))
        before = before.replace('<h3><a href="/home/existingrooms/public">Or view public rooms</a></h3>', '<h3><a href="/home/existingrooms">Or view private rooms</a></h3>').replace("<h2>Private Rooms</h2>", "<h2>Public Rooms</h2>")
        for file in listdir(join(directory, "chat")):
            if isdir(join(directory, "chat", file)):
                f = open(join(directory, "chat", file, "config.txt"))
                config = f.read().split("\n")

                if config[1] == "yes":
                        seconds = int(time()-float(config[4]))
                        days = seconds // seconds_in_day
                        hours = (seconds - (days * seconds_in_day)) // seconds_in_hour
                        minutes = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour)) // seconds_in_minute
                        template = f'<a href="/home/{file}" style="text-decoration: none; color: inherit"><pre id="chat" class="chat" style="width: 400px; height: 175px; border: 10px solid rgb(73, 73, 73); padding: 10px; overflow: auto; white-space:pre-wrap; display: inline-block; vertical-align: top;"><h2>{config[0]}</h2><h3>Created {days} day(s), {hours} hour(s) and {minutes} minute(s)  ago.</h3></pre></a>'

                        before = before.replace("<!-- {templatehere} -->", f"<!-- {{templatehere}} -->\n{template}")
        return before
    
    @app.route("/home/existingrooms/archives")
    def existingarchives():
        return getcontents(join("home", "join_room", "archives.html"), True, request.cookies.get("theme"))

class signup:
    @app.route("/testsignup", methods=['GET', 'POST'])
    def testsignup():
        username = request.form['username']
        password = request.form['password']
        lowerusername = username.lower()

        try:
            if request.cookies.get("accountcreated") != None:

                seconds_in_day = 60 * 60 * 24
                if time()-float(request.cookies.get("accountcreated")) < seconds_in_day/2:
                    seconds_in_hour = 60 * 60
                    seconds_in_minute = 60
                    
                    seconds = (seconds_in_day-(time()-float(request.cookies.get("accountcreated"))))/2

                    days = seconds // seconds_in_day
                    hours = (seconds - (days * seconds_in_day)) // seconds_in_hour
                    minutes = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour)) // seconds_in_minute
                    return errormessage("/signup", f"You have already created an account today. Please wait {round(days)} day(s), {round(hours)} hour(s) and {round(minutes)} minute(s)")
        except: pass

        if lowerusername in notallowedusernames:
            return errormessage("/signup", "That username is not allowed")
        if int(len(password)) < 3:
            return errormessage("/signup", "Password is too short")
        if int(len(username)) < 4:
            return errormessage("/signup", "Username is too short")
        elif int(len(username)) > 16:
            return errormessage("/signup", "Username is too long")
        for symbol in notallowed:
            if symbol in username:
                return errormessage("/signup", "An illegal character is in the username")
        for item in profanitylist:
            if item != "" and item != " ":
                if item in lowerusername:
                    return errormessage("/signup", "Username was flagged by profanity filter")

        currentusers, temp, temp = getusernames()
        lowercaseusers = []
        for user in currentusers:
            lowercaseusers.append(user.lower())
        if lowerusername in lowercaseusers:
            return errormessage("/signup", "Username is already taken")
        
        try:
            mkdir(join(storage, "userinfo", username))
        except NotADirectoryError:
            return errormessage("/signup", "Invalid username")
        except FileExistsError:
            pass
        open(join(storage, "userinfo", username, "info.txt"), "w").close()
        open(join(storage, "userinfo", username, "friends.txt"), "w").close()

        f = open(join(storage, "users.txt"), "a")
        salt = uuid.uuid4().hex
        hashed_password = customhash(password + salt)
        f.write(f'\n{{"username": "{username}", "password": "{hashed_password}", "salt": "{salt}"}}')
        f.close()
        setuserinfo(username, "accountcreation", time())

        log(f"{request.remote_addr} signed up with username '{username}' and password '{password}'") # Remove pass after debug
        
        token = uuid.uuid4().hex + uuid.uuid4().hex + uuid.uuid4().hex + uuid.uuid4().hex
        loggedin.append(f"{username}:{token}")
        return f"<script>document.cookie = \"Token={token}; path=/\";\ndocument.cookie=\"accountcreated={time()};\"\nwindow.location=\"/home\";</script>" # account created is a temp solution to alts
 
    @app.route("/signup")
    def signup():
        if request.cookies.get("TOS") == "0" or request.cookies.get("TOS") == None:
            return "<script>window.location=\"/TOS\"</script>"
        if request.cookies.get("updatetime") != str(startuptime): # Change once I get to keep user data
            return "<script>window.location=\"/newupdates\"</script>"
        return getcontents("signup/index.html", True, request.cookies.get("theme"))

class login:
    @app.route("/testlogin", methods=['GET', 'POST'])
    def testlogin():
        username = request.form['username']
        password = request.form['password']
        # users = getusers()

        # adminusers, adminpass, adminsalts = getusernames("admins.txt")
        usernames, passwords, salts = getusernames()
        
        # if username in adminusers:      
        #     salt = adminsalts[adminusers.index(username)]
        #     hashed_password = customhash(password + salt)
        #     token = None
        #     if hashed_password == adminpass[adminusers.index(username)]:
        #         for user in loggedin:
        #             user = user.split(":")
        #             if user[0] == username:
        #                 token = user[1]
        #         if token == None:
        #             token = uuid.uuid4().hex + uuid.uuid4().hex + uuid.uuid4().hex + uuid.uuid4().hex
        #             loggedin.append(f"{username}:{token}")
        #         return f"<script>document.cookie = \"Token={token}; path=/\"\nwindow.location=\"/home\";</script>"
                
        if username in usernames:
            salt = salts[usernames.index(username)]   
            hashed_password = customhash(password + salt)
            token = None
            if hashed_password == passwords[usernames.index(username)]:
                for user in loggedin:
                    user = user.split(":")
                    if user[0] == username:
                        token = user[1]
                if token == None:
                    token = uuid.uuid4().hex + uuid.uuid4().hex + uuid.uuid4().hex + uuid.uuid4().hex
                    loggedin.append(f"{username}:{token}")
                return f"<script>document.cookie = \"Token={token}; path=/\"\nwindow.location=\"/home\";</script>"
            else:
                return errormessage("/index.html", "Incorrect password")
        else:
            return errormessage("/index.html", "Username not found")

class audio:
    @app.route("/audio/<sound>")
    def mainaudio(sound):
        return getbytes(join(storage, "audio", "notification.wav"))
class fonts:
    @app.route("/fonts/<font>")
    def mainfont(font):
        return getbytes(join(storage, "fonts", font))


if __name__ == "__main__":
    log("Started Flask Server", log=True)
    app.run(port=80) # Certificate: app.run(ssl_context=(join("https", "cert.pem"), join("https", "key.pem")))
    #socketio.run(app)   
    
