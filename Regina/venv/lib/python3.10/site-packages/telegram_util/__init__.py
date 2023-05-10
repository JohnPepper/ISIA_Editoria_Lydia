#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import traceback as tb
import urllib.request
import threading
from bs4 import BeautifulSoup
import requests
import re
import time
import datetime as dt
import sys
import os
import unicodedata

name = 'telegram_util'

def hasSeq(text, sequences):
    if not text:
        return False
    for seq in sequences:
        index = 0
        for char in seq:
            index = text.find(char, index)
            if index == -1:
                break
        if index != -1:
            return True
    return False

def isprintable(s):
    try: 
        s.encode('utf-8')
    except UnicodeEncodeError: return False
    else: return True

def cutCaptionHtml(text, limit):
    text = ''.join([c for c in text if isprintable(c)])
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)
    for _ in range(20):
        text = text.replace('\n\n\n', '\n\n')
    if len(text) <= limit:
        return text
    lines = text.split('\n')
    count = 0
    for ind, line in enumerate(lines):
        count += 1 + len(line)
        if count > limit:
            break
    return '\n'.join(lines[:ind]).strip()

def removeOldFiles(dirname, day = 3):
    try:
        os.listdir(dirname)
    except:
        return 0
    count = 0 
    for filename in os.listdir(dirname):
        if os.path.getmtime(dirname + '/' + filename) < time.time() - 60 * 60 * 24 * day:
            os.system("rm '%s'" % (dirname + '/' + filename))
            count += 1
    return count

def parseDomain(url):
    if not url:
        return 
    if not url.startswith('http'):
        return
    r = '/'.join(url.split('/')[:3])
    if r.count('/') == 2 and 'http' in r:
        return r

def commitRepo(delay_minute = 1, commit_message = 'auto_commit_db'):
    commands = [
        'git add .',
        'git commit -m ' + commit_message,
        'git fetch origin', 
        'git rebase origin/master',
        'git push -u -f',
    ]
    command = ' && '.join([x + ' > /dev/null 2>&1' for x in commands])
    if delay_minute == 0:
        os.system(command)
    else:
        threading.Timer(60 * delay_minute, lambda: os.system(command)).start()

def cnWordCount(x):
    if not x:
        return 0
    return len([c for c in x if c.isalpha() and ord(c) > 255])

def getLogStr(*args):
    return ' '.join([str(x) for x in args])

def log(*args):
    text = getLogStr(*args)
    with open('nohup.out', 'a') as f:
        f.write('%d:%d %s\n' % (dt.datetime.now().hour, dt.datetime.now().minute, text))

class AlbumResult(object):
    def __init__(self):
        self.imgs = []
        self.cap = ''
        self.video = ''
        self.cap_html = '' # weibo status only
        self.title = '' # weibo status only
        self.wid = '' # weibo status only 
        self.rwid = '' # weibo status only retweet id
        self.hash = ''
        self.url = ''
        self.cap_html_v2 = ''
        self.no_parse = False

    def getParseMode(self):
        if self.no_parse:
            return
        if self.cap_html_v2:
            return 'HTML'
        if self.cap_html and 'weibo' not in self.url:
            return 'HTML'
        return 'Markdown'

    def empty(self):
        return (not self.imgs) and (not self.cap) and (not self.video) and (not self.cap_html_v2)

    def toPlain(self):
        new_album = AlbumResult()
        new_album.imgs = self.imgs
        new_album.video = self.video
        if self.imgs or self.video:
            limit = 1000 - len(self.url) - 10
        else:
            limit = 4000 - len(self.url) - 10
        if self.cap_html_v2:
            new_album.cap_html_v2 = cutCaptionHtml(self.cap_html_v2, limit) + '\n\n' + self.url
        elif self.cap or self.imgs or self.video:
            new_album.cap = cutCaptionHtml(self.cap, limit) + '\n\n' + self.url
        return new_album

    def __str__(self):
        return '\t'.join([k + ':' + str(v) for (k,v) in self.__dict__.items() if v])

def compactText(text):
    for _ in range(10):
        text = text.replace('  ', ' ')
        text = text.replace('\r', '\n')
        text = text.replace('\n ', '\n')
        text = text.replace(' \n', '\n')
        text = text.replace('\xa0', ' ')
    text = text.replace('\n', '\n\n')   
    for _ in range(20): 
        text = text.replace('\n\n\n', '\n\n')
    return text.strip()

def compactTextV2(text):
    for _ in range(10):
        text = text.replace('  ', ' ')
        text = text.replace('\r', '\n')
        text = text.replace('\n ', '\n')
        text = text.replace(' \n', '\n')
        text = text.replace('\xa0', ' ')
    for _ in range(20): 
        text = text.replace('\n\n\n', '\n\n')
    return text.strip()

def escapeMarkdown(text):
    in_bracket = False
    r = []
    for x in text:
        if x in ['[', '(']:
            in_bracket = True
        if x in [')', ']']:
            in_bracket = False
        if not in_bracket and x == '_':
            r.append("\\")
        r.append(x)
    text = ''.join(r)
    for special_char in ['`', '*', 'https://', 'http://']:
        text = text.replace(special_char, '')
    text = text.replace('t.cn/', ' t.cn/')
    return compactText(text)

def getWid(url):
    url = clearUrl(url)
    if 'id=' in url:
        return url[url.find('id=') + 3:].split('&')[0]
    return url.split('/')[-1]
        
def cutCaption(quote, suffix, limit):
    quote = quote.strip()
    suffix = suffix.strip()
    if not quote:
        result = suffix
    elif len(quote) + len(suffix) > limit:
        result = quote[:limit - len(suffix)] + '... ' + suffix
    else:
        result = quote + ' ' + suffix
    return escapeMarkdown(result)

def isCN(title):
    if re.search(u'[\u4e00-\u9fff]', title):
        return True
    return False

def isArab(text):
    for c in text:
        name = unicodedata.name(c).lower()
        if 'arabic' in name or 'persian' in name:
            return True
    return False

TO_CLEAN = '#/?'
def cleanFileName(name):
    for x in TO_CLEAN:
        name = name.replace(x, '')
    if name.split()[0][-1:] == ':':
        name = name.replace(':', ' ', 1)
    return name[:50]

def getSoup(url):
    headers = {'Host':'telete.in',
        'Connection':'keep-alive',
        'Cache-Control':'max-age=0',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
        'Sec-Fetch-User':'?1',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Sec-Fetch-Site':'none',
        'Sec-Fetch-Mode':'navigate',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'en-US,en;q=0.9,zh;q=0.8,zh-CN;q=0.7'}
    r = requests.get(url, headers=headers)
    return BeautifulSoup(r.text, 'html.parser')

def isInt(item):
    try:
        int(item)
        return True
    except:
        return False

def getChat(bot, text):
    text = text.split('/')[-1]
    if not text.startswith('@') and not isInt(text):
        text = "@" + text
    return bot.getChat(text)

def getDisplayChat(chat):
    if chat.username:
        return '[' + chat.title + '](t.me/' + str(chat.username) + ')'
    else:
        return chat.title

def getDisplayChatHtml(chat):
    if chat.username:
        return '<a href="%s">%s</a>' % ('t.me/' + str(chat.username), chat.title)
    else:
        return chat.title

def formatChat(bot, chat_id):
    try:
        chat = bot.getChat(chat_id)
        return getDisplayChat(chat)
    except:
        return str(chat_id)

def log_on_fail(debug_group = None, error_to_ignore=[]):
    def decorate(f):
        def applicator(*args, **kwargs):
            try:
                return f(*args,**kwargs)
            except Exception as e:
                if str(e) in error_to_ignore:
                    return
                print(e)
                tb.print_exc()
                if debug_group:
                    debug_group.send_message(text=str(e)) 
                    try:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        debug_group.send_message(''.join(
                            tb.format_tb(exc_traceback)))
                    except Exception as e:
                        debug_group.send_message(text=str(e)) 
        return applicator
    return decorate

def getDisplayUser(user):
    result = ''
    if user.first_name:
        result += user.first_name
    if user.last_name:
        result += ' ' + user.last_name
    if user.username:
        result += ' (' + user.username + ')'
    return '[' + result + '](tg://user?id=' + str(user.id) + ')'

def getDisplayUserHtml(user):
    result = ''
    if user.first_name:
        result += user.first_name
    if user.last_name:
        result += ' ' + user.last_name
    if user.username:
        result += ' (' + user.username + ')'
    return '<a href="%s">%s</a>' % ('tg://user?id=' + str(user.id), result)

def splitCommand(text):
    if not text:
        return '', ''
    pieces = text.split()
    if len(pieces) < 1:
        return '', ''
    command = pieces[0]
    return command.lower(), text[text.find(command) + len(command):].strip()

def tryDelete(msg): 
    try:    
        msg.delete()    
    except: 
        pass

def autoDestroy(msg, minutes=1):
    if msg.chat_id > 0:
        return
    threading.Timer(minutes * 60, lambda: tryDelete(msg)).start() 

class WaitTimer():
    def __init__(self):
        self.timer = {}

    def wait(self, key, sec):
        time.sleep(max(0, self.timer.get(key, 0) - time.time()))
        self.timer[key] = time.time() + sec
wait_timer = WaitTimer()

class TimedDeleter():
    def __init__(self):
        self.queue = []

    def process(self):
        new_queue = []
        while self.queue:
            t, msg = self.queue.pop()
            if t < time.time():
                tryDelete(msg)
            else:
                new_queue.append((t, msg))
        self.queue = new_queue
        if not self.queue:
            return
        self.queue.sort()
        self.schedule()

    def delete(self, msg, minutes=0):
        if minutes < 0.1:
            return tryDelete(msg)
        delete_time = time.time() + minutes * 60
        self.queue.append((delete_time, msg))
        if len(self.queue) == 1:
            self.schedule()

    def schedule(self):
        time_gap = min(self.queue[0][0] - time.time() + 30, 5 * 60)
        threading.Timer(time_gap, lambda: self.process()).start() 

def getMatchedKey(t, keys):
    if not t:
        return []
    result = []
    for key in keys:
        if str(key).lower() in str(t).lower():
            result.append(key)
    return result

def matchKey(t, keys):
    if not t:
        return False
    for k in keys:
        if str(k).lower() in str(t).lower():
            return True
    return False

def isUrl(t):
    for key in ['telegra.ph', 'com/', 'org/', '.st/', 'http', 't.co/']:
        if key in t:
            return True
    return False

def parseUrl(t):
    r = t
    for x in t.split():
        if not isUrl(x):
            continue
        if '://' in x:
            x = x[x.find('://') + 3:]
        else:
            r = r.replace(x, 'https://'+ x)
        for s in x.split('/'):
            if '?' in s:
                continue
            r = r.replace(s, urllib.request.pathname2url(s))
    return r

def isMeaningful(msg):
    if msg.media_group_id:
        return False
    if msg.text and 'bot_ignore' in msg.text:
        return False
    if msg.photo or msg.document or msg.video or msg.poll:
        return True
    if not msg.text:
        return False
    if msg.text[0] == '/':
        return False
    return len(msg.text) > 10

def _getFile(msg):
    file = None
    if msg.photo:
        file = msg.photo[-1]
    elif msg.video:
        file = msg.video
    if not file:
        return
    return file.get_file()

def getFilePath(msg):
    file = _getFile(msg)
    if file:
        return file.file_path

def getTmpFile(msg):
    file = _getFile(msg)
    if not file:
        return
    filename = 'tmp' + file.file_path.strip().split('/')[-1]
    file.download(filename)
    return filename

def addToQueue(update, queue, subscription):
    msg = update.effective_message 
    if not msg or not msg.chat:
        return
    if msg.chat.id not in subscription:
        return
    queue.append((msg.chat.id, msg.message_id))

def getLinkFromMsg(msg):
    for item in msg.entities:
        if matchKey(item["type"], ['url', 'link']):
            url = msg.text[item["offset"]:][:item["length"]]
            if not '://' in url:
                url = "https://" + url
            return url

def clearUrl(url):
    if not url:
        return ''
    for end_char in ['/?utm_source', '?mblogid', '&chksm=', 
            '&amp;chksm=', '&scene=21']:
        url = url.split(end_char)[0]
    if not matchKey(url, ['id=']):
        url = url.split('#')[0]
    if matchKey(url, ['weibo', 'thepaper', 'm.sohu']) and 'id=' not in url: 
        url = url.split('?')[0]
    if matchKey(url, ['/s/']):
        url = url.split('?')[0]
    return url.strip('/')

def getChannelsLog(channels):
    result = []
    for channel in channels:
        if channel.id > 0:
            result.append(getDisplayUserHtml(channel))
        else:
            result.append(getDisplayChatHtml(channel))
    result.sort()
    return 'channels: ' + ' '.join(result)

def getBasicLog(msg):
    result = ['id: %d' % msg.chat.id]
    if msg.from_user:
        if msg.chat.id != msg.from_user.id:
            result.append('user_id: %d' % msg.from_user.id)
        result.append('user: ' + getDisplayUserHtml(msg.from_user))
    if msg.chat.id < 0:
        result.append('chat: ' + getDisplayChatHtml(msg.chat))
    result.append('content: ' + msg.text_html_urled)
    return ' '.join(result)

def getTitleFromText(text):
    text = text.strip().split('\n')[0].strip()
    text = text.split('。')[0]
    if text.startswith('【'):
        new_text = text.split('】')[0][1:]
        if len(new_text) > 5:
            text = new_text
    text = text.strip()
    if text.endswith('source'):
        text = text[:-6].strip()
    if not text.startswith('【网评】'):
        text = text.split('【网评】')[0]
    if text.endswith('】') and text.startswith('【'):
        text = text[1:-1]
    if text.startswith('【'):
        index = text.rfind('】')
        if index != -1:
            text = text[1 :index + 1] + '【' + text[index + 1:]
    if text.endswith('】'):
        index = text.find('【')
        if index != -1:
            text = text[:index] + '】' + text[index:-1] 
    return text.replace('#', '')

def wait_when_need(func):
    try:
        return func()
    except Exception as e:
        if 'Timed out' in str(e):
            return
        if str(e).endswith('seconds'):
            wait = int(str(e).split()[-2])
            time.sleep(wait + 5)
            return func()
        raise e

def send_message(chat, message, parse_mode='markdown'):
    try:
        return wait_when_need(lambda: chat.send_message(message, disable_web_page_preview=True, parse_mode=parse_mode))
    except Exception as e:
        return wait_when_need(lambda: chat.send_message(message, disable_web_page_preview=True))

def isMastodonUrl(url):
    return len(url.split('/')) == 5 and isInt(url.split('/')[4]) and url.split('/')[3].startswith('@')