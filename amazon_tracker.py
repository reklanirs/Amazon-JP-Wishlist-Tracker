#!/usr/local/bin/python3
# -*- coding: utf-8 -*- 


import os,re,sys,time
import subprocess,shlex
import math,random
import requests,json
import configparser


'''
'cookie' is not needed in header if your wishlist is public.
Only tested on Amazon Japan
'''

#sys.stdin=open('in.txt','r')
wish_list = ''
threshold = '' # How much discount you want
cookie = ''
ifttt_webhook = '' # get it from https://ifttt.com/services/maker_webhooks/settings

items = []


def read_config():
    global wish_list,threshold, cookie, ifttt_webhook
    config = configparser.RawConfigParser()
    config.read('config.ini')
    for i in config['DEFAULT']:
        print(i,config['DEFAULT'][i])
    wish_list = config['DEFAULT']['wish_list']
    threshold = config['DEFAULT']['threshold']
    cookie = config['DEFAULT']['cookie']
    ifttt_webhook = config['DEFAULT']['ifttt_webhook']
    if len(cookie)<=10 or cookie[-3:]=='xxx':
        cookie = ''
    pass

def mail(msg):
    payload = { 'value1' : msg.replace('\n','<br>'), 'value2': threshold}
    r = requests.post(ifttt_webhook, data = payload)
    print(r.text)


def filter_sales():
    l = []
    percentage = lambda x: float(x.strip('%'))/100
    for title,price,discount in items:
        if discount!='0' and percentage(discount) >= percentage(threshold):
            l.append((title,price,discount))
            print('%s\t%s\t%s'%(title,price,discount))
    print('%d items are bigger than threshold.'%len(l))
    for title,price,discount in l:
        print('%s\t%s\t%s'%(title,price,discount))
    return l

def extract_title_price_discount(t):
    global items
    indx = t.find('次の中から検索') if '次の中から検索' in t else 0
    ret = []
    while indx!=-1:
        indx = t.find('title="', indx)
        # print(t[indx:indx+100])
        if indx == -1:
            break
        title = t[indx + 7:t.find('"', indx + 8)]
        indx = t.find('a-offscreen', indx + 10)
        price = t[indx + len('a-offscreen">￥') : t.find('<', indx + len('a-offscreen">￥') )].replace(',','')
        discount = '0'
        if '価格が' in t[indx : indx + 1500]:
            indx = t.find('価格が', indx)
            discount = t[indx + len('価格が'): t.find('下がりました', indx)]
            if discount[-1] != '%':
                discount = round(int(discount[1:].replace(',',''))*100.0/int(price))
                if discount == 0:
                    discount = '0'
                else:
                    discount = str(discount) + '%'
        # print('%s\t%s\t%s'%(title,price,discount))
        ret.append((title,price,discount))
    items += ret
    return ret


def main():
    read_config()

    headers = {
        'authority': 'www.amazon.co.jp',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'referer': 'https://www.amazon.co.jp/hz/wishlist/ls/XO10RB290A7V?&sort=default',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en,ja;q=0.9,zh;q=0.8,zh-TW;q=0.7,zh-CN;q=0.6',
        'cookie': cookie,
    }

    params = (
        ('', ''),
        ('sort', 'default'),
    )
    
    r = requests.get(wish_list,  headers=headers, params=params)
    # print(r.text)
    num = 0
    while True:
        extract_title_price_discount(r.text)
        for i in r.text.split('\n'):
            if '追加された商品' in i:
                # print(i)
                # print('\n\n\n\n\n')
                num +=1

        if 'もっと見る' not in r.text:
            break
        reg = re.findall(r'lek=.+?&', r.text)
        t = reg[0]
        lek = t[4:-1]
        print('lek:' ,lek)
        params = (
            ('filter', 'DEFAULT'),
            ('viewType', 'list'),
            ('lek', lek),
            ('sort', 'default'),
            ('type', 'wishlist'),
            ('ajax', 'true'),
        )
        r = requests.get(wish_list,  headers=headers, params=params)
        # time.sleep(1)
    pass
    print('\nTotal items in the wish list:', num)
    print('%d items are on sale:'%sum([0 if k=='0' else 1 for i,j,k in items]))
    for title,price,discount in items:
        if discount!='0':
            print('%s\t%s\t%s'%(title,price,discount))
    l = filter_sales()
    msg = ''
    msg += '%d items are bigger than threshold:\n\n'%len(l)
    for title,price,discount in l:
        msg += '\t%s\t%s\t%s\n'%(title,price,discount)
    mail(msg)

if __name__ == '__main__':
    main()
