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
import multiprocessing
import ConfigParser

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
        print ('cookie already exist, try login with cookie')
        cookie_jar = cookielib.LWPCookieJar(cookie_file)
        cookie_jar.load(ignore_discard=True, ignore_expires=True)
        cookie_support = urllib2.HTTPCookieProcessor(cookie_jar)
        opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
        #login_url = 'http://huaban.com/auth/'
        login_url = 'http://huaban.com/'
        data = urllib2.urlopen(login_url).read()
        with open('huaban-login-succeed.html','w+') as fd:
            fd.write(data)
            print ('login end')
        return 0
    print ('cookie not exist,try login with username and password')
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
        print ('login fail ,try agian?')
        return
    text = result.read()

    print ("****")
    print (text)
    #login_url = 'http://huaban.com/'
    #data = urllib2.urlopen(login_url).read()

    cookie_jar2.save(cookie_file, ignore_discard=True, ignore_expires=True)
    #with open('huaban-login-succeed.html','w+') as fd:
    #    fd.write(data)
    return 1

def get_config(section, name):
    config = ConfigParser.ConfigParser()
    config.readfp(open(config_file, 'r'))
    try:
        tmp = config.get(section, name)
        return tmp
    except ConfigParser.NoOptionError:
        print ('ERROR: config file not complete!')
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
    #it's not a good idea to set a start maxid manually, but i still not find a good way to get this value
    maxid = 1931195482
    linkfd = open('board_link.txt', 'a+')
    while True:
        parse_url = 'http://huaban.com/boards/%s/?ip1cygfp&max=%s&limit=100&wfl=1' % (str(board),str(maxid))
        req_imgurl = urllib2.Request(
            url=parse_url,
            headers=http_headers
        )
        print (parse_url)
        try:
            content = urllib2.urlopen(req_imgurl,timeout = 30).read()
            time.sleep(0.8)
        except:
            print ('parse board fail %s' % board)
            continue
        #print content
        with open(store_json_file,'w+') as fd:
            fd.write(content)
        if len(content)<50:
            print ('total count %d'%count)
            print ('this board get done')
            return 0
        with open(store_json_file, 'r') as fds:
            try:
                js = json.load(fds)
            except:
                print ('something wrong with json parsed ')
                maxid -= 1
                continue
            if not js['board']['pins']:
                print ('total count %d' % count)
                print ('this board get done')
                return 0
            for i in js['board']['pins']:
                pin = i['file'].get('key')
                if pin:
                    maxid = i.get('pin_id')
                    count += 1
                    print (pin)
                    linkfd.write('http://hbimg.b0.upaiyun.com/')
                    linkfd.write(pin)
                    linkfd.write('\n')
            print ('count %d' % count)
def get_pic_by_url( links = [], *args ):
    """
    get pic and store it and rename it by its img type
    arg;links should be a list
    """
    trytic = 0
    print (type(links))
    print links
    http_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',}
    for link in links:
        print (link  + time.asctime())
        req_imgurl = urllib2.Request(
            url=link,
            headers=http_headers
        )
        while True:
            try:
                content = urllib2.urlopen(req_imgurl, timeout=20).read()
                with open(os.path.join(img_store_path, link[len('http://hbimg.b0.upaiyun.com/'):]), 'wb+') as ifd:
                    ifd.write(content)
                rename_Img_file_by_type(os.path.join(img_store_path, link[len('http://hbimg.b0.upaiyun.com/'):]))
                break
            except:
                trytic += 1
                if (trytic % 3) == 0:
                    break
                print ('parse img fail %s' % link)
                print ('try again')
def get_pic_by_lines( start, end,file, *args ):
    """
    get pic and store it and rename it by its img type
    arg;links should be a list
    """
    #print ('%s %s %s'%(start, end, file))
    print ('thread pid %d'%os.getpid())
    http_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
    if not os.path.exists(img_store_path):
        os.mkdir(img_store_path)
    with open(file,'r') as fd:
        for i, line in enumerate(fd):
            if i >= start and i <= end:
                link = line[:-1]
                print (link + time.asctime())
                req_imgurl = urllib2.Request(
                    url=link,
                    headers=http_headers
                )
                trytic = 0
                while True:
                    try:
                        content = urllib2.urlopen(req_imgurl, timeout=20).read()
                        #print 'data download ok'
                        with open(os.path.join(img_store_path, link[len('http://hbimg.b0.upaiyun.com/'):]), 'wb+') as ifd:
                            ifd.write(content)
                        rename_Img_file_by_type(os.path.join(img_store_path, link[len('http://hbimg.b0.upaiyun.com/'):]))
                        break
                    except:
                        trytic += 1
                        if (trytic % 3) == 0:
                            break
                        print ('parse img fail %s' % link)
                        print ('try again')
                        continue

def get_huaban_pic_by_file(file):
    threadmax = get_config('scrapy_settings', 'thread_number')
    threadmax = int(threadmax)
    links_before = []
    fd = open(file, 'r')
    if not fd:
        print ('ERROR pic link file not exist')
        return 1
    http_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',}
    count = 0
    # it is not safe here,
    while True:
        link = fd.readline()
        if not link:
            break
        links_before.append(link.split('\n')[0])
    links = remove_dumplicate_list(links_before)
    del links_before[:]
    print ('total pic %d' % len(links))
    check_img_exist(links, img_store_path)
    print ('total pic after remove duplicate img %d' % len(links))
    if len(links) >= threadmax:
        filper = len(links) // threadmax
        i = 0
        while i < len(links):
            try:
                pro = multiprocessing.Process(target=get_pic_by_lines, args=(i, i+filper-1,file))
                pro.start()
                #pro.join()
                i = i + filper
            except:
                print ('something err when start mutiprocess')
                continue
    tail = len(links) % threadmax
    if tail:
        get_pic_by_lines(len(links)-tail,len(links)-1,file)
def rename_Img_file_by_type(filepath):
    tail = imghdr.what(filepath)
    if tail:
        if filepath[-(len(tail)+1):] == ('.'+tail):
            print ('already in right tail')
            return
        os.rename(filepath, filepath + '.' + tail)
def check_img_exist(filelinks = [], storepath = ''):
    dellist = []
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
def remove_dumplicate_list(seq = []):
    seen = set()
    seen_add = seen.add
    tmp = [x for x in seq if not (x in seen or seen_add(x))]
    print ('after remove %d' % len(tmp))
    return tmp
if __name__ == '__main__':
    do_login('huaban.cookie')
    if len(sys.argv) > 1:
        for i in sys.argv[1:]:
            print ('get board %d'%int(i))
            get_huaban_by_board(i)
            print ('get link record done, you should rerun this program again without args to download those imgs')
    else:
        if not os.path.exists(get_config('login_account_info', 'link_file')):
            print ('ERROR! link file not exist, you should parse by enter board first')
            exit(1)
        get_huaban_pic_by_file(get_config('login_account_info', 'link_file'))
        print ('end of scrap')
