import os
import sys
import urllib
import urllib2
import cookielib
import base64
import re
import hashlib
import json
import binascii
import time
import imghdr
import sys
import platform
import threading
import ConfigParser
import socket
import time

store_json_file = 'huaban.json'
config_file = 'huaban_config.ini'
img_store_path = 'img'


def do_login(cookie_file):
    """"
    Perform login action with use name, password and saving cookies.
    @param username: login user name
    @param pwd: login password
    @param cookie_file: file name where to save cookies when login succeeded
    """
    login_data = dict()
    login_data['email'] = get_config('login_account_info', 'login_username')
    login_data['password'] = get_config('login_account_info', 'login_password')
    login_data['_ref'] = 'frame'
    if os.path.exists(cookie_file):
        log_huaban('cookie already exist, try login with cookie')
        cookie_jar = cookielib.LWPCookieJar(cookie_file)
        cookie_jar.load(ignore_discard=True, ignore_expires=True)
        cookie_support = urllib2.HTTPCookieProcessor(cookie_jar)
        opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
        # login_url = 'http://huaban.com/auth/'
        login_url = 'http://huaban.com/'
        data = urllib2.urlopen(login_url).read()
        with open('huaban-login-succeed.html','w+') as fd:
            fd.write(data)
            log_huaban('login end')
        return 0
    log_huaban('cookie not exist,try login with username and password')
    cookie_jar2 = cookielib.LWPCookieJar()
    cookie_support2 = urllib2.HTTPCookieProcessor(cookie_jar2)
    opener2 = urllib2.build_opener(cookie_support2, urllib2.HTTPHandler)
    urllib2.install_opener(opener2)
    login_url = 'https://huaban.com/auth/'

    login_data = urllib.urlencode(login_data)
    http_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',
                    'Access-Control-Request-Headers': 'x-request,x-requested-with',
                    'Origin': 'http://huaban.com',
                    'Connection': 'keep-alive',
                    'Host': 'huaban.com',
                    '(Request-Line)': 'OPTIONS /auth/ HTTP/1.1',
                    }
    req_login = urllib2.Request(
        url=login_url,
        data=login_data,
        headers=http_headers
    )
    try:
        result = urllib2.urlopen(req_login, timeout=20)
    except urllib2.URLError:
        log_huaban('login fail ,try again?')
        return
    text = result.read()

    # login_url = 'http://huaban.com/'
    # data = urllib2.urlopen(login_url).read()

    cookie_jar2.save(cookie_file, ignore_discard=True, ignore_expires=True)
    # with open('huaban-login-succeed.html','w+') as fd:
    #    fd.write(data)
    return 1


def get_config(section, name):
    config = ConfigParser.ConfigParser()
    config.readfp(open(config_file, 'r'))
    try:
        tmp = config.get(section, name)
        return tmp
    except ConfigParser.NoOptionError:
        log_huaban('ERROR: config file not complete!')
        return None


def get_huaban_by_board(board):
    http_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',
                    'Origin': 'http://huaban.com',
                    'Host': 'huaban.com',
                    '(Request-Line)': 'GET /boards/%s/?ip1cygfp&max=931195482&limit=100&wfl=1 HTTP/1.1' % (str(board)),
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': 'http://huaban.com/boards/%s/' % (str(board)),
                    'X-Request': 'JSON',
                    }
    count = 0
    # it's not a good idea to set a start max_id manually, but i still not find a good way to get this value
    max_id = 1931195482
    linkfd = open('board_link.txt', 'a+')
    while True:
        parse_url = 'http://huaban.com/boards/%s/?ip1cygfp&max=%s&limit=100&wfl=1' % (str(board),str(max_id))
        req_img_url = urllib2.Request(
            url=parse_url,
            headers=http_headers
        )
        log_huaban(parse_url)
        try:
            content = urllib2.urlopen(req_img_url, timeout=30).read()
            time.sleep(0.8)
        except:
            e = sys.exc_info()[0]
            log_huaban(('parse board fail %s, info %s' % (board, str(e))), 0)
            continue
        # log_huabancontent
        with open(store_json_file,'w+') as fd:
            fd.write(content)
        if len(content) < 50:
            log_huaban('total count %d'% count)
            log_huaban('this board get done')
            return 0
        with open(store_json_file, 'r') as fds:
            try:
                js = json.load(fds)
            except:
                log_huaban('something wrong with json parsed ')
                max_id -= 1
                continue
            if not js['board']['pins']:
                log_huaban('total count %d' % count)
                log_huaban('this board get done')
                return 0
            for i in js['board']['pins']:
                pin = i['file'].get('key')
                if pin:
                    max_id = i.get('pin_id')
                    count += 1
                    log_huaban(pin)
                    linkfd.write('http://hbimg.b0.upaiyun.com/')
                    linkfd.write(pin)
                    linkfd.write('\n')
            log_huaban('count %d' % count)
            
            
def get_pic_by_url(link, *args ):
    """
    get pic and store it and rename it by its img type
    arg;links should be a list
    """
    if type(link) == list:
        links = link
    else:
        links = list()
        links.append(link)
    try_count = 0
    http_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',}
    for link in links:
        log_huaban(link + time.asctime())
        req_img_url = urllib2.Request(
            url=link,
            headers=http_headers
        )
        while True:
            try:
                content = urllib2.urlopen(req_img_url, timeout=20).read()
                with open(os.path.join(img_store_path, link[len('http://hbimg.b0.upaiyun.com/'):]), 'wb+') as ifd:
                    ifd.write(content)
                rename_img_file_by_type(os.path.join(img_store_path, link[len('http://hbimg.b0.upaiyun.com/'):]))
                break
            except:
                try_count += 1
                if (try_count % 3) == 0:
                    break
                log_huaban('parse img fail %s' % link)
                log_huaban('try again')
                
                
def get_pic_by_lines( start, end, file, *args):
    """
    get pic and store it and rename it by its img type
    arg;links should be a list
    """
    global gTotalImgProCnt
    global gStopFlag
    log_huaban('thread pid %d' % os.getpid())
    http_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
    if not os.path.exists(img_store_path):
        os.mkdir(img_store_path)
    # in case undefined arg
    tmp_file_path = 'xx'
    with open(file,'r') as fd:
        for idx, line in enumerate(fd):
            if start <= idx <= end:
                link = line[:-1]
                log_huaban(link + time.asctime())
                req_img_url = urllib2.Request(
                    url=link,
                    headers=http_headers
                )
                try_count = 0
                while True:
                    if gStopFlag:
                        log_huaban('received stop flag, thread[%d] quit' % os.getpid(), 1)
                        return
                    try:
                        content = urllib2.urlopen(req_img_url, timeout=20).read()
                        tmp_file_path = os.path.join(img_store_path, link[len('http://hbimg.b0.upaiyun.com/'):])
                        with open(tmp_file_path, 'wb+') as ifd:
                            ifd.write(content)
                        rename_img_file_by_type(tmp_file_path)
                        gTotalImgProCnt += 1
                        break
                    except urllib2.HTTPError:
                        e = sys.exc_info()[0]
                        log_huaban('parse fail.. %s for %s' % (str(e), link))
                        try_count += 1
                        if try_count > 3:
                            log_huaban(('parse img fail %s' % link), 1)
                            break
                    except KeyboardInterrupt:
                        log_huaban('keyboard except, thread %d quit' % os.getpid(), 1)
                        return
                    except:
                        e = sys.exc_info()[0]
                        # record emergency unknow error
                        log_huaban(('ERROR:%s' % str(e)), 0)
                        # remove tmp_file
                        if os.path.exists(tmp_file_path) and os.path.isfile(tmp_file_path):
                            os.remove(tmp_file_path)
                        # don't harsh, rest a while
                        time.sleep(3)
                        pass

gThreadMutexLog = threading.Lock()
gLogLevel = 2
gTotalImgProCnt = 0
gStopFlag = False


def log_huaban(str_info, level=3):
    global gLogLevel
    global gThreadMutexLog
    if level <= gLogLevel:
        gThreadMutexLog.acquire()
        print(str_info)
        gThreadMutexLog.release()

    pass

                        
def get_huaban_pic_by_file(file):
    global gTotalImgProCnt
    global gStopFlag
    set_max_thread = get_config('scrapy_settings', 'thread_number')
    set_max_thread = int(set_max_thread)
    links_before = []
    fd = open(file, 'r')
    if not fd:
        log_huaban('ERROR pic link file not exist')
        return 1
    count = 0
    # it is not safe here,
    while True:
        link = fd.readline()
        if not link:
            break
        links_before.append(link.split('\n')[0])
    links = remove_duplicate_list(links_before)
    del links_before[:]
    log_huaban(('total pic %d' % len(links)))
    check_img_exist(links, img_store_path)
    log_huaban(('total pic after remove duplicate img %d' % len(links)))
    child_process_list = list()
    gStopFlag = False
    if len(links) >= set_max_thread:
        filper = len(links) // set_max_thread
        idx = 0
        while idx < len(links):
            try:
                pro = threading.Thread(target=get_pic_by_lines, args=(idx, idx+filper-1,file))
                pro.setDaemon(False)
                pro.start()
                child_process_list.append(pro)
                # pro.join()
                idx += filper
            except:
                log_huaban('something err when start thread', 0)
                continue
    tail = len(links) % set_max_thread
    if tail:
        pro = threading.Thread(target=get_pic_by_lines, args=(len(links)-tail, len(links)-1, file))
        pro.setDaemon(False)
        pro.start()
        # get_pic_by_lines(len(links)-tail,len(links)-1,file)
    tmp_link_file = get_config('login_account_info', 'link_file')
    while True:
        try:
            all_exist = True
            for child_pro in child_process_list:
                if child_pro.is_alive():
                    all_exist = False
                    break
            if all_exist:
                log_huaban('All Task Done, quit..' ,0)
                os.remove(tmp_link_file)
                return
            time.sleep(2)
            rec_cnt_start = gTotalImgProCnt
            time.sleep(1)
            rec_cnt_end = gTotalImgProCnt
            log_huaban('%d pic/s' % (rec_cnt_end - rec_cnt_start), 1)
        except KeyboardInterrupt:
            log_huaban('keyboard int, manually quit!', 0)
            gStopFlag = True
            exit(0)


def rename_img_file_by_type(filepath):
    tail = imghdr.what(filepath)
    if tail:
        if filepath[-(len(tail)+1):] == ('.'+tail):
            log_huaban('already in right tail')
            return
        new_file_path = filepath + '.' + tail
    else:
        log_huaban(('Warning:img type not recognize!%s' % filepath))
        log_huaban('we assume is to be jpg')
        new_file_path = filepath + '.' + 'jpg'
    if not os.path.exists(new_file_path):
        os.rename(filepath, new_file_path)
        
        
def check_img_exist(file_links, storepath):
    dellist = []
    filelinks = list()
    if not os.path.exists(storepath):
        log_huaban('store dir not exist, create it.')
        os.mkdir(storepath)
        return filelinks
    for file in os.listdir(storepath):
        for link in filelinks:
            if link.split('/')[-1] == file.split('.')[0]:
                dellist.append(link)
    for link in dellist:
        try:
            filelinks.remove(link)
        except:
            pass
    return filelinks


def remove_duplicate_list(seq):
    seen = set()
    seen_add = seen.add
    tmp = [x for x in seq if not (x in seen or seen_add(x))]
    log_huaban(('after remove %d' % len(tmp)))
    return tmp


def main():
    do_login('huaban.cookie')
    if len(sys.argv) > 1:
        for idx in sys.argv[1:]:
            log_huaban(('get board %d'% int(idx)))
            get_huaban_by_board(idx)
            log_huaban('get links done, rerun program again without args to download those imgs')
    else:
        if not os.path.exists(get_config('login_account_info', 'link_file')):
            log_huaban('ERROR! link file not exist, you should parse by enter board first')
            exit(1)
        get_huaban_pic_by_file(get_config('login_account_info', 'link_file'))
        log_huaban('end of scrap')

if __name__ == '__main__':
    main()
