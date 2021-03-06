#coding:utf-8
import urllib2
import io
import random
import urllib
from bs4 import BeautifulSoup
import re
import os
import lxml
import requests
from lxml import etree

import sys
reload(sys)
sys.setdefaultencoding('utf8')

def GetHtml(url):
    if len(url) < 1:
        return ''
    print 'the spider work with --->>>' + str(url)
    user_agent = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:50.0) Gecko/20100101 Firefox/50.0'
        # 'Mozilla/5.0 (Windows NT 5.2) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.122 Safari/534.30',
        # 'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0',
        # 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET4.0E; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)',
        # 'Opera/9.80 (Windows NT 5.1; U; zh-cn) Presto/2.9.168 Version/11.50',
        # 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1',
        # 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022; .NET4.0E; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)'        
    ]
    #set web encoding, get chinese string
    encoding = "gb18030"
    #make http header，set user-agent
    header = {"User-Agent":random.choice(user_agent)}
    #make request with head
    request = urllib2.Request(url,headers=header)
    #get request result
    html = urllib2.urlopen(request).read()
    #use beautifulSoup to deal with html page,like dom
    soup = BeautifulSoup(html,'lxml')
    # print str(soup)
    return soup

#requests post url,get html same with firefox see
def GetRequestPost(url):
    data = requests.post(url)
    soup = BeautifulSoup(data.text,'lxml')
    return soup

####xpath to parse and get first classified list
def GetMainMarket(url):
    soup = GetHtml(url)
    xpathfile = etree.HTML(str(soup))
    lname = xpathfile.xpath('//ul[@class="service-bd"]/li/span/a/text()')
    lhref = xpathfile.xpath('//ul[@class="service-bd"]/li/span/a/@href')
    return InputChooice(lname, lhref)


#get detail classified list, same to GetDetail but use xpath
def GetDetailMarket(url):
    temp = GetDetail(url)           #too much different format to get detail classified list
    # soup = GetRequestPost(temp)   #totalPage=1
    soup = GetHtml(temp)            #totalPage normal
    lnum = int( re.findall('"pager":{"pageSize":60,"totalPage":(\d*),"currentPage"',str(soup))[0] )
    # xpathfile = etree.HTML(str(soup))
    return temp,lnum

########use re to parse , had been deprecated
#search taobao.com, get classified and analyze next url
def GetClassified(url):
    soup = GetHtml(url)
    a = re.findall('data-dataid="\d*"\shref="([a-zA-z]+://[^\s]*)">([^\s]*)<',str(soup))
    # a = re.findall('data-dataid="\d*"\shref="([a-zA-z]+://[^\s]*)">([^\u4e00-\u9fa5]*)',str(soup))
    utype = []
    ulink = []
    for x in xrange(0,len(a)):
        utype.append(a[x][1])
        ulink.append(str(a[x][0]))
    return InputChooice(utype, ulink)

def GetDetail(url):
    soup = GetHtml(url)
    # a = re.findall('href="([a-zA-z]+://[^\s]*)">([^\u4e00-\u9fa5]*)<',str(soup))
    # a = re.findall('{"cat_name":"([^\s]*)","cat_href":"([a-zA-z]+://[^\s]*)"}{1}',str(soup)])
    a = re.findall('{"cat_name":"[^\u4e00-\u9fa5]*","cat_href":"[\S]*}',str(soup))
    b = re.findall('"name":"[\w]*[^\u4e00-\u9fa5]*","link":"[\S]*"}]',str(soup))
    t = []
    name = []
    link = []
    if len(a) > 0:
        for x1 in xrange(0,len(a)):
            a1 = re.findall('(.+?)\}\,\{', str(a[x1]))
            for x2 in xrange(0,len(a1)):
                t.append(a1[x2])

        for x3 in xrange(0,len(t)):
            # print str(x3) + t[x3]
            # print str(re.findall('cat_name":"(.*)","cat_href"',t[x3]))
            # print '\n'
            # name.append(re.findall('cat_name":"([^\u4e00-\u9fa5]*)",',t[x3])[0])
            name.append(re.findall('cat_name":"(.*)","cat_href"',t[x3])[0])
            # link.append(re.findall('cat_href":"(.*)"',t[x3])[0])
            if (re.findall('cat_href":"(.*)"',t[x3])[0]).find("https://") >= 0 :
                link.append(re.findall('cat_href":"(.*)"',t[x3])[0])
            else:
                link.append((re.findall('cat_href":"(.*)"',t[x3])[0].replace('//', 'https://') ) )
        # print link
        return InputChooice(name, link)
    elif len(b) > 0:
        for x1 in xrange(0,len(b)):
            b1 = re.findall('(.+?)},{', str(b[x1]))
            for x2 in xrange(0,len(b1)):
                t.append(b1[x2])
        print '\n'
        # print t
        for x3 in xrange(0,len(t)):
            print str(x3) + t[x3]
            print str(re.findall('name":"(.*)","link"',t[x3]))
            # name.append(re.findall('cat_name":"([^\u4e00-\u9fa5]*)",',t[x3])[0])
            name.append(re.findall('name":"(.*)","link"',t[x3])[0])
            # link.append(re.findall('cat_href":"(.*)"',t[x3])[0])
            if (re.findall('link":"(.*)"',t[x3])[0]).find("https://") >= 0 :
                link.append(re.findall('link":"(.*)"',t[x3])[0])
            else:
                link.append((re.findall('link":"(.*)"',t[x3])[0].replace('//', 'https://') ) )
            print link[x3]
            print '\n'

    else:
        print 'no more choice, you can get picture in this url :' + str(url)
        exit()


if __name__ == "__main__":
    url = 'https://s.taobao.com/'

    ########### xpath
    # link = GetMainMarket(url)
    # pic_link = GetDetailMarket(link)
    # num = raw_input("你需要爬取多少页？\n")
    # for x in xrange(0,int(num)):
    #     GetPic(pic_link)
    #     pic_link = GetNextPage(pic_link)

    ########### re
    # clink = GetClassified(url)
    # piclink = GetDetail(clink)
    # if len(piclink) > 1:
    #     picstart = GetPic(piclink)
    # print picorigin
