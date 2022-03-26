import requests , traceback, os, sys,json, psutil, time, jdatetime, pytz
from pyrogram import Client , filters
from pyrogram.errors import *
from pyrogram.raw import functions
from pyrogram.raw import types
from pyrogram.types import Message

def get_cmd_param(cmd_str,cmd_len,param_num=50,param_spacer=" "):
    try:
        param0=cmd_str[cmd_len:]
        param= []
        param1=param0.strip()
        param2 = param1.split(param_spacer, cmd_len + 1)
        for i in range(len(param2)):
            if param2[i] != "":
                param.append(param2[i].strip())
        if param_num > len(param):
            param_num = len(param)
        return param[0:param_num]
    except Exception as err_param:
        print(str(err_param))
        a=traceback.print_exc()
def refresh_watch():
    global watch_latest
    try:
        if (os.stat("data/watch.json").st_size == 0):
            with open("data/watch.json", "w") as write_file:
                write_file.write("[]")
        with open("data/watch.json", "r") as read_file:
            watch_latest = json.load(read_file)
    except FileNotFoundError as e:
        with open("data/watch.json", "w") as write_file:
            write_file.write("[]")

refresh_watch()
admincmds=["checkbot","sysusage","chatlist","watchlist","addwatch","delwatch","help"]
app = Client("myappapi" , config_file="deploy.ini")
@app.on_message(filters.me & filters.text & ~filters.edited & ~filters.forwarded, group=0)
async def main(client , m:Message):
    try:
        admintext=m.text.strip()
        chat_info=m.chat
        if admintext=="/checkbot":
            refresh_watch()
            if not m.reply_to_message:
                await m.edit(f"**{admintext}**\n**BOT : I'm on!**")
        elif admintext=="/sysusage":
            cpu_info = psutil.cpu_times_percent()
            cpu_usage=cpu_info[0]
            memory = psutil.virtual_memory()
            await m.edit(f"**{admintext}**\n\n**System usage information:**\nCpu usage: {cpu_usage}%\nMemory usage: {memory[2]}%")
        elif admintext[:7]=="/chlist":

            #get all chats as a chats object
            a = await app.send(
                functions.messages.GetAllChats(except_ids=[])
            )

            # select chats field from the whole object and load as json
            chlist = json.loads(str(a["chats"]))
            chlist_clear = []
            for i in chlist:
                # i_obj = await app.get_chat(i["id"])
                # i_type = i_obj.type
                templist={"id":i["id"], "title":i["title"]}
                # templist = i
                chlist_clear.append(templist)

            # write the last modified json to a json file 
            with open("data/chlist.json", "w") as write_file:
                json.dump(chlist_clear, write_file, ensure_ascii=False, indent=4, skipkeys=True, allow_nan=True)
            await app.send_document("me", "data/chlist.json", caption="All Chats List")
            refresh_watch()
        elif admintext[:10]=="/watchlist":

            # Return back the json file content, containing the list of watching chats, 
            try:
                await app.send_document("me", "data/watch.json", caption="All Watching Chats List")
                
            # Or an error, saying the watch list is empty
            except Exception:
                    await app.send_message("me", "Watch list file is not located\nDatabase will be rebuilt")
            refresh_watch()
        elif admintext[:10]=="/addwatch ":
            ch_params = get_cmd_param(admintext, 10, 2)
            chid = ch_params[0]
            chtype = ch_params[1] if len(ch_params) > 1 else "channel"
            if str.isdecimal(chid):
                try:
                    chatobj = await app.get_chat(int(chid))
                except Exception:
                    print("Error resolving chat id int")
            else:
                try:
                    chatobj = await app.get_chat(chid)
                except Exception:
                    print("Error resolving chat id str")
            if not "chatobj" in locals():
                await app.send_message("me", "Invalid chat id!")
            else:
                if chatobj.type == chtype:
                    chtitle = chatobj.title
                    chid = chatobj.id
                    chtype = chatobj.type
                    with open("data/watch.json", "r") as read_file:
                        watching = json.load(read_file)
                    newrecord = {"id":chid , "title": chtitle, "type": chtype}
                    watchnew = []
                    for i in watching:
                        if not (i["id"] == newrecord["id"] and i["type"] == newrecord["type"]):
                            templist = {"id": i["id"] , "title": i["title"], "type": i["type"]}
                            watchnew.append(templist)
                    watchnew.append(newrecord)
                    with open("data/watch.json", "w") as write_file:
                        json.dump(watchnew, write_file, ensure_ascii=False, indent=4,   skipkeys=True, allow_nan=True)
                    await app.send_message("me", "Record added to watching list successfully!")
                else:
                    await app.send_message("me", "**Found a chat, but invalid chat type!**\n Supported types: group, supergroup, channel")
                refresh_watch()
        elif admintext[:10]=="/delwatch ":
            ch_params = get_cmd_param(admintext, 10, 2)
            chid = ch_params[0]
            chtype = ch_params[1] if len(ch_params) > 1 else "channel"
            if str.isdecimal(chid):
                try:
                    chatobj = await app.get_chat(int(chid))
                except Exception:
                    await app.send_message("me", "Invalid chat id number!")
            else:
                try:
                    chatobj = await app.get_chat(chid)
                except Exception:
                    await app.send_message("me", "Invalid chat id string!")
            if not "chatobj" in locals():
                pass
            else:
                if chatobj.type == chtype:
                    chid = chatobj.id
                    chtype = chatobj.type
                    chtitle = chatobj.title
                    with open("data/watch.json", "r") as read_file:
                        watching = json.load(read_file)
                    watchnew = []
                    for i in watching:
                        if i["type"] == chtype:
                            if i["id"] == chid:
                                pass
                            else:
                                templist = {"id": i["id"] , "title": i["title"], "type": i["type"]}
                                watchnew.append(templist)
                        else:
                            templist = {"id": i["id"] , "title": i["title"], "type": i["type"]}
                            watchnew.append(templist)
                    # write the last modified json to a json file 
                    with open("data/watch.json", "w") as write_file:
                        json.dump(watchnew, write_file, ensure_ascii=False, indent=4, skipkeys=True, allow_nan=True)
                    await app.send_message("me", "Record deleted from watching list successfully!")
                else:
                    await app.send_message("me", "**Found a chat, but invalid chat type!**\n Supported types: group, supergroup, channel")
            refresh_watch()
        elif admintext[:5]=="/help":
            await app.send_message("me", "HELP TEXT HERE!")
            # if admintext=="/help":
            #     await app.send_document("me", "data/chlist.json", caption="Full Help")
            # elif admintext[:6] == "/help "
            #     arg = get_cmd_param(admintext, 6, 1)[0]
            #     if arg in admincmds:
            #         print()
    except Exception as all_err:
        await app.send_message("me", f"Command has rised an error : **{admintext}**\nExc_info: {sys.exc_info()[0]}\n{sys.exc_info()[1]}\n{sys.exc_info()[2]}\n{sys.exc_info()[2].tb_frame}\n{sys.exc_info()[2].tb_lasti}\nLine: {sys.exc_info()[2].tb_lineno}\n{sys.exc_info()[2].tb_next}")

@app.on_message(group=1)
async def main(client , m:Message):
    global watch_latest
    chatid = m.chat.id
    for j in watch_latest:
        if chatid == j["id"]:
            await m.forward("me")
app.run()