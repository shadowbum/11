from cProfile import run
import pstats
from pyobigram.utils import sizeof_fmt,get_file_size,createID,nice_time
from pyobigram.client import ObigramClient,inlineQueryResultArticle
from MoodleClient import MoodleClient

from JDatabase import JsonDatabase
import shortener
import zipfile
import os
import infos
import xdlink
import mediafire
import datetime
import time
import youtube
import NexCloudClient
from pydownloader.downloader import Downloader
from ProxyCloud import ProxyCloud
import ProxyCloud
import socket
import tlmedia
import S5Crypto
import asyncio
import aiohttp
from yarl import URL
import re
import random
from draft_to_calendar import send_calendar
import moodlews

listproxy = []

def sign_url(token: str, url: URL):
    query: dict = dict(url.query)
    query["token"] = token
    path = "webservice" + url.path
    return url.with_path(path).with_query(query)

def nameRamdom():
    populaton = 'abcdefgh1jklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    name = "".join(random.sample(populaton,10))
    return name

def downloadFile(downloader,filename,currentBits,totalBits,speed,time,args):
    try:
        bot = args[0]
        message = args[1]
        thread = args[2]
        if thread.getStore('stop'):
            downloader.stop()
        downloadingInfo = infos.createDownloading(filename,totalBits,currentBits,speed,time,tid=thread.id)
        bot.editMessageText(message,downloadingInfo)
    except Exception as ex: print(str(ex))
    pass

def uploadFile(filename,currentBits,totalBits,speed,time,args):
    try:
        bot = args[0]
        message = args[1]
        originalfile = args[2]
        thread = args[3]
        downloadingInfo = infos.createUploading(filename,totalBits,currentBits,speed,time,originalfile)
        bot.editMessageText(message,downloadingInfo)
    except Exception as ex: print(str(ex))
    pass

def processUploadFiles(filename,filesize,files,update,bot,message,thread=None,jdb=None):
    try:
        bot.editMessageText(message,'#Login #Moodle\nPreparing for upload')
        evidence = None
        fileid = None
        user_info = jdb.get_user(update.message.sender.username)
        cloudtype = user_info['cloudtype']
        proxy = ProxyCloud.parse(user_info['proxy'])
        draftlist=[]
        if cloudtype == 'moodle':
        	host = user_info['moodle_host']
        	user = user_info['moodle_user']
        	passw = user_info['moodle_password']
        	token = moodlews.get_webservice_token(host,user,passw)
        	print(token)
        	for file in files:
        		data = asyncio.run(moodlews.webservice_upload_file(host,token,file,progressfunc=uploadFile,proxy=proxy,args=(bot,message,filename,thread)))
        		while not moodlews.store_exist(file):pass
        		data = moodlews.get_store(file)
        		if data:
        		    urls = moodlews.make_draft_urls(data)
        		    draftlist.append({'file':file,'url':urls[0]})
        	return draftlist
        elif cloudtype == 'cloud':
            tokenize = False
            if user_info['tokenize']!=0:
               tokenize = True
            host = user_info['moodle_host']
            user = user_info['moodle_user']
            passw = user_info['moodle_password']
            remotepath = user_info['dir']
            client = NexCloudClient.NexCloudClient(user,passw,host,proxy=proxy)
            loged = client.login()
            bot.editMessageText(message,'#Uploading #Nextcloud\nPlease wait')
            if loged:
               originalfile = ''
               if len(files)>1:
                    originalfile = filename
               filesdata = []
               for f in files:
                   data = client.upload_file(f,path=remotepath,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                   filesdata.append(data)
                   os.unlink(f)                
               return filesdata
        return None
    except Exception as ex:
        bot.editMessageText(message,f'#Error\n{str(ex)}')


def processFile(update,bot,message,file,thread=None,jdb=None):
    user_info = jdb.get_user(update.message.sender.username)
    name =''
    if user_info['rename'] == 1:
        ext = file.split('.')[-1]
        if '7z.' in file:
            ext1 = file.split('.')[-2]
            ext2 = file.split('.')[-1]
            name = nameRamdom() + '.'+ext1+'.'+ext2
        else:
            name = nameRamdom() + '.'+ext
    else:
        name = file
    os.rename(file,name)
    file_size = get_file_size(name)
    getUser = jdb.get_user(update.message.sender.username)
    max_file_size = 1024 * 1024 * getUser['zips']
    file_upload_count = 0
    client = None
    findex = 0
    if file_size > max_file_size:
        compresingInfo = infos.createCompresing(name,file_size,max_file_size)
        bot.editMessageText(message,compresingInfo)
        zipname = str(name).split('.')[0] + createID()
        mult_file = zipfile.MultiFile(zipname,max_file_size)
        zip = zipfile.ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
        zip.write(name)
        zip.close()
        mult_file.close()
        client = processUploadFiles(name,file_size,mult_file.files,update,bot,message,jdb=jdb)
        try:
            os.unlink(name)
        except:pass
        file_upload_count = len(zipfile.files)
    else:
        client = processUploadFiles(name,file_size,[name],update,bot,message,jdb=jdb)
        file_upload_count = 1
    bot.editMessageText(message,'#TXT\nPreparing file')
    evidname = ''
    files = []
    if client:
        if getUser['cloudtype'] == 'moodle':
            if getUser['uploadtype'] == 'evidence':
                try:
                    evidname = str(name).split('.')[0]
                    txtname = evidname + '.txt'
                    evidences = client.getEvidences()
                    for ev in evidences:
                        if ev['name'] == evidname:
                           files = ev['files']
                           break
                        if len(ev['files'])>0:
                           findex+=1
                    client.logout()
                except:pass
            if getUser['uploadtype'] == 'draft' \
                    or getUser['uploadtype'] == 'perfil' \
                    or getUser['uploadtype'] == 'blog' \
                    or getUser['uploadtype'] == 'calendar'\
                    or getUser['uploadtype'] == 'calendarevea':
               for draft in client:
                   files.append({'name':draft['file'],'directurl':draft['url']})
        else:
            for data in client:
                files.append({'name':data['name'],'directurl':data['url']})
        if user_info['urlshort']==1:
            if len(files)>0:
                i = 0
                while i < len(files):
                    files[i]['directurl'] = shortener.short_url(files[i]['directurl'])
                    i+=1
        bot.deleteMessage(message.chat.id,message.message_id)
        finishInfo = infos.createFinishUploading(name,file_size,max_file_size,file_upload_count,file_upload_count,findex)
        filesInfo = infos.createFileMsg(name,files)
        bot.sendMessage(message.chat.id,finishInfo+'\n'+filesInfo,parse_mode='html')
        if len(files)>0:
            txtname = str(name).split('/')[-1].split('.')[0] + '.txt'
            sendTxt(txtname,files,update,bot)
    else:
        bot.editMessageText(message,'#Error')

def ddl(update,bot,message,url,file_name='',thread=None,jdb=None):
    downloader = Downloader()
    file = downloader.download_url(url,progressfunc=downloadFile,args=(bot,message,thread))
    if not downloader.stoping:
        if file:
            processFile(update,bot,message,file,jdb=jdb)

def sendTxt(name,files,update,bot):
                txt = open(name,'w')
                fi = 0
                for f in files:
                    separator = ''
                    if fi < len(files)-1:
                        separator += '\n'
                    txt.write(f['directurl']+separator)
                    fi += 1
                txt.close()
                bot.sendFile(update.message.chat.id,name)
                os.unlink(name)

def onmessage(update,bot:ObigramClient):
    try:
        thread = bot.this_thread
        username = update.message.sender.username
        tl_admin_user = 'Abolanos3'

        #set in debug
        tl_admin_user = 'Abolanos3'

        jdb = JsonDatabase('database')
        jdb.check_create()
        jdb.load()

        user_info = jdb.get_user(username)
        #if username == tl_admin_user or user_info:
        if username in str(tl_admin_user).split(';') or user_info :  # validate user
            if user_info is None:
                #if username == tl_admin_user:
                if username == tl_admin_user:
                    jdb.create_admin(username)
                else:
                    jdb.create_user(username)
                user_info = jdb.get_user(username)
                jdb.save()
        else:
            mensaje = "Access dennied"
            intento_msg = "#Access\nThe user @"+username+ " has tried to access"
            bot.sendMessage(update.message.chat.id,mensaje)
            bot.sendMessage(958475767,intento_msg)
            return


        msgText = ''
        try: msgText = update.message.text
        except:pass

        # comandos de admin
        if '/add' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    jdb.create_user(user)
                    jdb.save()
                    msg = 'The user ['+user+'] has being added!'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,'#Error\nMissing 1 required positional argument: {user}')
            else:
                bot.sendMessage(update.message.chat.id,'Administrator permissions requiered')
            return
        if '/admin' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    jdb.create_admin(user)
                    jdb.save()
                    msg = 'Now @'+user+' is an administrator!'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,'#Error\nMissing 1 required positional argument: {user}')
            else:
                bot.sendMessage(update.message.chat.id,'Administrator permissions requiered')
            return
        if '/addproxy' in msgText:
            isadmin = jdb.is_admin(username)
            global listproxy
            if isadmin:
                try:
                    proxy = str(msgText).split(' ')[1]
                    listproxy.append(proxy)
                    zize = len(listproxy)-1
                    bot.sendMessage(update.message.chat.id,f'Proxy Registrado en la Posicion {zize}')
                except:
                    bot.sendMessage(update.message.chat.id,'#Error\nMissing 1 required positional argument: {proxy}')
            else:
                bot.sendMessage(update.message.chat.id,'Administrator permissions requiered')
            return
        if '/check_proxy' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    msg = 'Proxys Registered\n'
                    cont = 0
                    for proxy in listproxy:
                        msg += str(cont) +'--'+proxy+'\n'
                        cont +=1
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,'#Error #Command\n/check_proxy')
            else:
                bot.sendMessage(update.message.chat.id,'Administrator permissions requiered')
            return
        if '/evea' == msgText:
            getUser = user_info
            user = ''
            passw = ''
            hostmo = 'https://evea.uh.cu/'
            zips = 240
            repoid = 4
            uptype = 'calendarevea' 
            if getUser:
                getUser['moodle_user'] = user
                getUser['moodle_password'] = passw
                getUser['moodle_host'] = hostmo
                getUser['zips'] = zips
                getUser['uploadtype'] = uptype
                getUser['moodle_repo_id'] = repoid
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,'Configuration loaded')
            return
        if '/eva' == msgText:
            getUser = user_info
            user = ''
            passw = ''
            hostmo = 'https://eva.uo.edu.cu/'
            zips = 99
            repoid = 4
            uptype = 'calendar' 
            if getUser:
                getUser['moodle_user'] = user
                getUser['moodle_password'] = passw
                getUser['moodle_host'] = hostmo
                getUser['zips'] = zips
                getUser['uploadtype'] = uptype
                getUser['moodle_repo_id'] = repoid
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,'Configuration loaded')
            return
        if '/cursos' == msgText:
            getUser = user_info
            user = ''
            passw = ''
            hostmo = 'https://cursos.uo.edu.cu/'
            zips = 99
            repoid = 4
            uptype = 'draft' 
            if getUser:
                getUser['moodle_user'] = user
                getUser['moodle_password'] = passw
                getUser['moodle_host'] = hostmo
                getUser['zips'] = zips
                getUser['uploadtype'] = uptype
                getUser['moodle_repo_id'] = repoid
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,'Configuration loaded')
            return
        if '/eduvirtual' == msgText:
            getUser = user_info
            user = ''
            passw = ''
            hostmo = 'https://eduvirtual.uho.edu.cu/'
            zips = 8
            repoid = 3
            uptype = 'blog' 
            if getUser:
                getUser['moodle_user'] = user
                getUser['moodle_password'] = passw
                getUser['moodle_host'] = hostmo
                getUser['zips'] = zips
                getUser['uploadtype'] = uptype
                getUser['moodle_repo_id'] = repoid
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,'Configuration loaded')
            return
        if '/uclv' == msgText:
            getUser = user_info
            user = ''
            passw = ''
            hostmo = 'https://moodle.uclv.edu.cu/'
            zips = 358
            repoid = 4
            uptype = 'calendar' 
            if getUser:
                getUser['moodle_user'] = user
                getUser['moodle_password'] = passw
                getUser['moodle_host'] = hostmo
                getUser['zips'] = zips
                getUser['uploadtype'] = uptype
                getUser['moodle_repo_id'] = repoid
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,'Configuration loaded')
            return
        if '/aula_uclv' == msgText:
            getUser = user_info
            user = ''
            passw = ''
            hostmo = 'https://aula.uclv.edu.cu/'
            zips = 358
            repoid = 5
            uptype = 'calendar' 
            if getUser:
                getUser['moodle_user'] = user
                getUser['moodle_password'] = passw
                getUser['moodle_host'] = hostmo
                getUser['zips'] = zips
                getUser['uploadtype'] = uptype
                getUser['moodle_repo_id'] = repoid
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,'Configuration loaded')
            return
        if '/short_url' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    for user in jdb.items:
                        if jdb.items[user]['urlshort']==0:
                            jdb.items[user]['urlshort'] = 1
                            continue
                        if jdb.items[user]['urlshort']==1:
                            jdb.items[user]['urlshort'] = 0
                            continue
                    jdb.save()
                    bot.sendMessage(update.message.chat.id,'Short URL changed')
                except:
                    bot.sendMessage(update.message.chat.id,'#Error #Command\n/short_url')
            return
        if '/remove' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    if user == username:
                        bot.sendMessage(update.message.chat.id,'You can not remove yourself')
                        return
                    jdb.remove(user)
                    jdb.save()
                    msg = 'User @'+user+' removed!'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,'#Error\nMissing 1 required positional argument: {user}')
            else:
                bot.sendMessage(update.message.chat.id,'Administrator permissions requiered')
            return
        if '/send_the_fucking_database' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                bot.sendMessage(update.message.chat.id,'#DB\nHere it is:')
                bot.sendFile(update.message.chat.id,'database.jdb')
            else:
                bot.sendMessage(update.message.chat.id,'Administrator permissions requiered')
            return
        # end

        # comandos de usuario
        if '/set_proxy' in msgText:
            getUser = user_info
            if getUser:
                try:
                   pos = int(str(msgText).split(' ')[1])
                   proxy = str(listproxy[pos])
                   getUser['proxy'] = proxy
                   jdb.save_data_user(username,getUser)
                   jdb.save()
                   msg = 'Su Proxy esta Listo'
                   bot.sendMessage(update.message.chat.id,msg)
                except:
                   bot.sendMessage(update.message.chat.id,'#Error\nMissing 1 required positional argument: {position}')
                return
        if '/info' in msgText:
            getUser = user_info
            if getUser:
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
                return
        if '/zips' in msgText:
            getUser = user_info
            if getUser:
                try:
                   size = int(str(msgText).split(' ')[1])
                   getUser['zips'] = size
                   jdb.save_data_user(username,getUser)
                   jdb.save()
                   msg = 'Size per parts: '+ sizeof_fmt(size*1024*1024)
                   bot.sendMessage(update.message.chat.id,msg)
                except:
                   bot.sendMessage(update.message.chat.id,'#Error\nMissing 1 required positional argument: {size}')
                return
        if '/acc' in msgText:
            try:
                #account = str(msgText).split(' ',2)[1].split(',')
                #user = account[0]
                #passw = account[1]
                user = str(msgText).split()[1]
                passw = str(msgText).split()[2]
                getUser = user_info
                if getUser:
                    getUser['moodle_user'] = user
                    getUser['moodle_password'] = passw
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,'Account saved')
            except:
                bot.sendMessage(update.message.chat.id,'#Error\nMissing required positional arguments: {user} or {passw}')
            return
        if '/host' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                host = cmd[1]
                getUser = user_info
                if getUser:
                    if 'http' in host:
                        getUser['moodle_host'] = host
                        jdb.save_data_user(username,getUser)
                        jdb.save()
                        statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                        bot.sendMessage(update.message.chat.id,'Host saved')
                    else:
                        bot.sendMessage(update.message.chat.id,'#Error\nArgument {host} is not an URL')
            except:
                bot.sendMessage(update.message.chat.id,'#Error\nMissing 1 required positional argument: {host}')
            return
        if '/repo' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                repoid = int(cmd[1])
                getUser = user_info
                if getUser:
                    getUser['moodle_repo_id'] = repoid
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'#Error\nMissing 1 required positional argument: {repoid}')
            return
        if '/rename_on' in msgText:
            try:
                getUser = user_info
                if getUser:
                    getUser['rename'] = 1
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,'Rename: On')
            except:
                bot.sendMessage(update.message.chat.id,'#Error #Command\n/rename_on')
            return
        if '/rename_off' in msgText:
            try:
                getUser = user_info
                if getUser:
                    getUser['rename'] = 0
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,'Rename: Off')
            except:
                bot.sendMessage(update.message.chat.id,'#Error #Command\n/rename_off')
            return
        if '/cloud' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                repoid = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['cloudtype'] = repoid
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'#Error\nMissing 1 required positional argument: {cloud}')
            return
        if '/uptype' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                type = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['uploadtype'] = type
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'#Error\nMissing 1 required positional argument: {type}')
            return
        if '/proxy' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                proxy = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['proxy'] = proxy
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,'Proxy saved')
            except:
                if user_info:
                    user_info['proxy'] = ''
                    statInfo = infos.createStat(username,user_info,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,'#Error\nSetting proxy')
            return
        if '/encrypt' in msgText:
            proxy_sms = str(msgText).split(' ')[1]
            proxy = S5Crypto.encrypt(f'{proxy_sms}')
            bot.sendMessage(update.message.chat.id, f'#Encryption #OK\nsocks5://{proxy}')
            return
        if '/decrypt' in msgText:
            proxy_sms = str(msgText).split(' ')[1]
            proxy_de = S5Crypto.decrypt(f'{proxy_sms}')
            bot.sendMessage(update.message.chat.id, f'#Decryption #OK\n{proxy_de}')
            return
        if '/dir' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                repoid = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['dir'] = repoid + '/'
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,'Directory saved')
            except:
                bot.sendMessage(update.message.chat.id,'#Error\nMissing 1 required positional argument: {directory}')
            return
        if '/cancel_' in msgText:
            try:
                cmd = str(msgText).split('_',2)
                tid = cmd[1]
                tcancel = bot.threads[tid]
                msg = tcancel.getStore('msg')
                tcancel.store('stop',True)
                time.sleep(3)
                bot.editMessageText(msg,'Task cancelled')
            except Exception as ex:
                print(str(ex))
            return
        #end

        message = bot.sendMessage(update.message.chat.id,'Analizyng')

        thread.store('msg',message)

        if '/start' in msgText:
            start_msg = 'Accesss guaranteed'
            bot.editMessageText(message,start_msg)
        elif '/files' == msgText and user_info['cloudtype']=='moodle':
             proxy = ProxyCloud.parse(user_info['proxy'])
             client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],proxy=proxy)
             loged = client.login()
             if loged:
                 files = client.getEvidences()
                 filesInfo = infos.createFilesMsg(files)
                 bot.editMessageText(message,filesInfo)
                 client.logout()
             else:
                bot.editMessageText(message,'#Error #Reasons\n- Host down\n- Wrong credentials')
        elif '/download' in msgText:
            try:
                url = str(msgText).split()[1]
                if 'http' in url:
                    ddl(update,bot,message,url,file_name='',thread=thread,jdb=jdb)
                else:
                    bot.editMessageText(message,'#Error\nArgument {url} is not an URL')
            except IndexError:
                bot.editMessageText(message,'#Error\nMissing 1 required positional argument: {url}')
        else:
            #if update:
            #    api_id = os.environ.get('api_id')
            #    api_hash = os.environ.get('api_hash')
            #    bot_token = os.environ.get('bot_token')
            #    
                # set in debug
            #    api_id = 9902519
            #    api_hash = '9d8097d05bbc90a6ed2a7a81abcd4e8a'
            #    bot_token = '5593646046:AAGHy6Z1PXmUWfnayr-r5Re7LqDT8HAF-k0'

            #    chat_id = int(update.message.chat.id)
            #    message_id = int(update.message.message_id)
            #    import asyncio
            #    asyncio.run(tlmedia.download_media(api_id,api_hash,bot_token,chat_id,message_id))
            #    return
            bot.editMessageText(message,'#Error\nAnalizyng message')
    except Exception as ex:
           print(str(ex))


def main():
    bot_token = '5593646046:AAGHy6Z1PXmUWfnayr-r5Re7LqDT8HAF-k0'
    print('init bot.')
    #set in debug
    bot_token = '5436610373:AAHfDAsYZ4w67_bvP3a1JZKDxDN6Kqi35gU'
    bot = ObigramClient(bot_token)
    bot.onMessage(onmessage)
    bot.run()

if __name__ == '__main__':
    try:
        main()
    except:
        main()
