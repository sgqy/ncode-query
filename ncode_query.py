#!/usr/bin/env python3

import urllib.request
import json
import re
import colorama
import datetime
import dateutil.parser

def last_update(date_str):
    time = dateutil.parser.parse(date_str)
    delta = datetime.datetime.now(datetime.timezone.utc) - time
    sec = int(delta.total_seconds())
    periods = [
        (colorama.Fore.RED     + '年' + colorama.Style.RESET_ALL, 60*60*24*365),
        (colorama.Fore.MAGENTA + '月' + colorama.Style.RESET_ALL, 60*60*24*30),
        (colorama.Fore.YELLOW  + '週' + colorama.Style.RESET_ALL, 60*60*24*7),
        (colorama.Fore.GREEN   + '日' + colorama.Style.RESET_ALL, 60*60*24),
        (colorama.Fore.CYAN    + '時' + colorama.Style.RESET_ALL, 60*60),
        (colorama.Fore.WHITE   + '分' + colorama.Style.RESET_ALL, 60),
        (colorama.Fore.WHITE   + '秒' + colorama.Style.RESET_ALL, 1),
    ]
    for p_name, p_sec in periods:
        if sec > p_sec:
            cnt, mod = divmod(sec, p_sec)
            return '{:2d} {}'.format(cnt, p_name)

def proc_info(data):
    j = json.loads(data)
    if j[0]['allcount'] == 0:
        print('[item 404]')
        return
    last = j[0]['allcount'] + 1
    if last > 501:
        last = 501
    for i in range(1, last):
        item = j[i]
    
        # color genre and ncode-link
        title = ''
        ncode = ''
        if item.get('nocgenre'):
            ncode = colorama.Fore.YELLOW + '{:7s}'.format(item['ncode'].lower()) + colorama.Style.RESET_ALL
            if item['nocgenre'] == 1:
                title = '[' + colorama.Fore.YELLOW  + '男性' + colorama.Style.RESET_ALL + ']'
            elif item['nocgenre'] == 2:
                title = '[' + colorama.Fore.CYAN    + '女性' + colorama.Style.RESET_ALL + ']'
            elif item['nocgenre'] == 3:
                title = '[' + colorama.Fore.RED    + 'ＢＬ' + colorama.Style.RESET_ALL + ']'
            elif item['nocgenre'] == 4:
                title = '[' + colorama.Fore.MAGENTA + '成年' + colorama.Style.RESET_ALL + ']'
            else:
                title = '[未知]'
        else:
            ncode = colorama.Fore.CYAN + '{:7s}'.format(item['ncode'].lower()) + colorama.Style.RESET_ALL
            title = '[' + colorama.Fore.GREEN + '一般' + colorama.Style.RESET_ALL + ']'

        # color title if it is single
        short = ''
        if item['noveltype'] == 1:
            short = colorama.Fore.WHITE
        elif item['noveltype'] == 2:
            short = colorama.Fore.YELLOW
        else:
            short = colorama.Fore.RED

        title += ' ' + short + item['title'] + colorama.Style.RESET_ALL

        # color status if the work is done or continue
        stat = ''
        if item['end'] == 0:
            stat = colorama.Fore.YELLOW + '完結済' + colorama.Style.RESET_ALL
        elif item['end'] == 1:
            stat = colorama.Fore.GREEN + '連載中' + colorama.Style.RESET_ALL
        else:
            stat = 'エラー'

        # calculate when is the last update
        last_str = item['novelupdated_at'] + ' +0900'
    
        print('[{:3d}][{}][{}][{}][{:10,}({:3d})]{}'.format(i, ncode, stat, last_update(last_str), item['length'], item['kaiwaritu'], title))

def proc_uri(uri):
    colorama.init() # windows only

    # the server will give EVERYTHING if empty
    if uri.endswith('='):
        return

    try:
        request = urllib.request.Request(uri, data=None, headers={})
        resp_fd = urllib.request.urlopen(request)
        data = resp_fd.read()
        resp_fd.close()
    except:
        print('\n[ex] ' + uri)
        exit()

    proc_info(data)

    colorama.deinit() # windows only

ncode_default = 'api/?of=n-l-w-t-e-nu-nt-ka-ng&out=json&lim=500'

r15_uri_g = 'https://api.syosetu.com/novelapi/' + ncode_default
r18_uri_g = 'https://api.syosetu.com/novel18api/' + ncode_default

r15_uri = r15_uri_g + '&ncode='
r18_uri = r18_uri_g + '&ncode='

ncode_re = '//(?P<type>.*)\.syosetu\.com/(?P<ncode>n[^/]*)/?'

def proc_ls(lines):
    r15 = r15_uri
    r18 = r18_uri
    for l in lines:
        m = re.search(ncode_re, l)
        if m:
            if m.group('type') == 'ncode':
                r15 += m.group('ncode') + '-'
            elif m.group('type') == 'novel18':
                r18 += m.group('ncode') + '-'
    print('R15 novel:')
    proc_uri(r15)
    print('R18 novel:')
    proc_uri(r18)

def proc_ls_sep(lines):
    for l in lines:
        m = re.search(ncode_re, l)
        if m:
            if m.group('type') == 'ncode':
                proc_uri(r15_uri + m.group('ncode'))
            elif m.group('type') == 'novel18':
                proc_uri(r18_uri + m.group('ncode'))
            else:
                print(l)
        else:
            print(l)


big_query_help = '''
query.py <type> <order>

type:
  t   短編
  r   連載中
  er  完結済連載小説
  re  連載小説
  ter 短編と完結済連載小説
order:
  new	新着更新順
  favnovelcnt   ブックマーク数の多い順
  reviewcnt     レビュー数の多い順
  hyoka         総合ポイントの高い順
  hyokaasc      総合ポイントの低い順
  impressioncnt 感想の多い順
  hyokacnt      評価者数の多い順
  hyokacntasc   評価者数の少ない順
  weekly        週間ユニークユーザの多い順
                毎週火曜日早朝リセット
                (前週の日曜日から土曜日分)
  lengthdesc    小説本文の文字数が多い順
  lengthasc     小説本文の文字数が少ない順
  ncodedesc     新着投稿順
  old	更新が古い順
'''

def proc_g(t, o):
    print('R15 novel:')
    proc_uri(r15_uri_g + '&type=' + t + '&order=' + o)
    print('R18 novel:')
    proc_uri(r18_uri_g + '&type=' + t + '&order=' + o)