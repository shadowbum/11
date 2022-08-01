from pyobigram.utils import sizeof_fmt,nice_time
import datetime
import time
import os

def text_progres(index,max):
	try:
		if max<1:
			max += 1
		porcent = index / max
		porcent *= 100
		porcent = round(porcent)
		make_text = ''
		index_make = 1
		make_text += '\n['
		while(index_make<21):
			if porcent >= index_make * 5: make_text+='█'
			else: make_text+='░'
			index_make+=1
		make_text += ']\n'
		return make_text
	except Exception as ex:
			return ''

def porcent(index,max):
    porcent = index / max
    porcent *= 100
    porcent = round(porcent)
    return porcent

def createDownloading(filename,totalBits,currentBits,speed,time,tid=''):
    msg = '#Downloading\n\n'
    msg+= 'File: ' + str(filename)+'\n'
    msg+= 'Download: ' + str(sizeof_fmt(currentBits)) + ' | ' + str(sizeof_fmt(totalBits)) + '\n'
    msg+= 'Speed: ' + str(sizeof_fmt(speed))+'/s\n'
    msg+= 'ETA: ' + str(datetime.timedelta(seconds=int(time))) +'\n\n'

    msg = '#Downloading\n\n'
    msg += 'File: '+filename+'\n'
    msg += 'Download: '+sizeof_fmt(currentBits)+' | '+sizeof_fmt(totalBits)+'\n'
    msg += 'Speed: '+sizeof_fmt(speed)+'/s\n'
    msg += 'ETA: '+str(datetime.timedelta(seconds=int(time)))+'s\n\n'

    if tid!='':
        msg+= '/cancel_' + tid
    return msg
def createUploading(filename,totalBits,currentBits,speed,time,originalname=''):
    msg = '#Uploading\n\n'
    msg+= 'File: ' + str(filename)+'\n'
    if originalname!='':
        msg = str(msg).replace(filename,originalname)
        msg+= 'Now: ' + str(filename)+'\n'
    msg+= 'Upload: ' + str(sizeof_fmt(currentBits))+' | '+str(sizeof_fmt(totalBits))+'\n'
    msg+= 'Speed: ' + str(sizeof_fmt(speed))+'/s\n'
    msg+= 'ETA: ' + str(datetime.timedelta(seconds=int(time))) +'\n'

    msg = '#Uploading\n\n'
    msg += 'File: '+filename+'\n'
    if originalname!='':
        msg = str(msg).replace(filename,originalname)
        msg+= 'Now: ' + str(filename)+'\n'
    msg += 'Upload: '+sizeof_fmt(currentBits)+' | '+str(sizeof_fmt(totalBits))+'\n'
    msg += 'Speed: '+sizeof_fmt(speed)+'/s\n'
    msg += 'ETA: '+str(datetime.timedelta(seconds=int(time)))+'s\n\n'

    return msg
def createCompresing(filename,filesize,splitsize):
    msg = '#Compressing\n\n'
    msg+= 'Total: ' + str(sizeof_fmt(filesize))+'\n'
    msg+= 'Zips: ' + str(sizeof_fmt(splitsize))+'\n'
    msg+= 'Amount of parts: ' + str(round(int(filesize/splitsize)+1,1))+'\n\n'
    return msg
    
def createFinishUploading(filename,filesize,split_size,current,count,findex):
    msg = '#Upload #OK\n\n'
    msg+= 'File: ' + str(filename)+'\n'
    msg+= 'Total: ' + str(sizeof_fmt(filesize))+'\n'
    msg+= 'Zips: ' + str(sizeof_fmt(split_size))+'\n'
    msg+= 'Uploaded parts: ' + str(current) + '/' + str(count) +'\n'
    return msg

def createFileMsg(filename,files):
    import urllib
    if len(files)>0:
        msg= '<b>Link</b>\n'
        for f in files:
            url = urllib.parse.unquote(f['directurl'],encoding='utf-8', errors='replace')
            #msg+= '<a href="'+f['url']+'"' + f['name'] + '</a>'
            msg+= "<a href='"+url+"'>"+f['name']+'</a>\n'
        return msg
    return ''

def createFilesMsg(evfiles):
    msg = 'Files ('+str(len(evfiles))+')\n\n'
    i = 0
    for f in evfiles:
            try:
                fextarray = str(f['files'][0]['name']).split('.')
                fext = ''
                if len(fextarray)>=3:
                    fext = '.'+fextarray[-2]
                else:
                    fext = '.'+fextarray[-1]
                fname = f['name'] + fext
                msg+= '/txt_'+ str(i) + ' /del_'+ str(i) + '\n' + fname +'\n\n'
                i+=1
            except:pass
    return msg
def createStat(username,userdata,isadmin):
    from pyobigram.utils import sizeof_fmt
    msg = '#User_info\n\n'
    msg+= 'Username: @' + username +'\n'
    msg+= 'User: ' + str(userdata['moodle_user'])+'\n'
    msg+= 'Password: ' + str(userdata['moodle_password']) +'\n'
    msg+= 'Host: ' + str(userdata['moodle_host'])+'\n'
    if userdata['cloudtype'] == 'moodle':
        msg+= 'Repo ID: ' + str(userdata['moodle_repo_id'])+'\n'
        msg+= 'Upload type: ' + str(userdata['uploadtype'])+'\n'
    msg += 'Cloud type: ' + str(userdata['cloudtype']) + '\n'
    if userdata['cloudtype'] == 'cloud':
        msg+= 'Directory: /' + str(userdata['dir'])+'\n'
    msg+= 'Zips : ' + sizeof_fmt(userdata['zips']*1024*1024) + '\n\n'
    msgAdmin = 'No'

    if isadmin:
        msgAdmin = 'Yes'
    msg+= 'Administrator : ' + msgAdmin + '\n'
    proxy = 'No'
    if userdata['proxy'] !='':
       proxy = 'Yes'
    rename = 'No'
    if userdata['rename'] == 1:
       rename = 'Yes'
    msg+= 'Rename : ' + rename + '\n'
    msg+= 'Proxy setted: ' + proxy + '\n'
    shorturl = (userdata['urlshort'] == 1)
    shortener = 'No'
    if shorturl:
       shortener = 'Yes'
    msg += 'Short URL: ' + shortener + '\n'
    return msg
