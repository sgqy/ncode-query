#!/usr/bin/env python3

import json
import re
import colorama
import datetime
import dateutil.parser
import multiprocessing
import fetch_data

def decode_genre(genre):
    periods = [
        # nothing
        (0, '????'),
        # nocgenre
        (1, colorama.Fore.YELLOW  + '男性' + colorama.Style.RESET_ALL),
        (2, colorama.Fore.CYAN    + '女性' + colorama.Style.RESET_ALL),
        (3, colorama.Fore.RED     + 'ＢＬ' + colorama.Style.RESET_ALL),
        (4, colorama.Fore.MAGENTA + '成年' + colorama.Style.RESET_ALL),
        # genre
        (101,  colorama.Fore.RED     + '　　異世界　　　' + colorama.Style.RESET_ALL),
        (102,  colorama.Fore.RED     + '　　現実世界　　' + colorama.Style.RESET_ALL),
        (201,  colorama.Fore.GREEN   + 'ハイファンタジー' + colorama.Style.RESET_ALL),
        (202,  colorama.Fore.GREEN   + 'ローファンタジー' + colorama.Style.RESET_ALL),
        (301,  colorama.Fore.YELLOW  + '　　純文学　　　' + colorama.Style.RESET_ALL),
        (302,  colorama.Fore.YELLOW  + 'ヒューマンドラマ' + colorama.Style.RESET_ALL),
        (303,  colorama.Fore.YELLOW  + '　　　歴史　　　' + colorama.Style.RESET_ALL),
        (304,  colorama.Fore.YELLOW  + '　　　推理　　　' + colorama.Style.RESET_ALL),
        (305,  colorama.Fore.YELLOW  + '　　ホラー　　　' + colorama.Style.RESET_ALL),
        (306,  colorama.Fore.YELLOW  + '　アクション　　' + colorama.Style.RESET_ALL),
        (307,  colorama.Fore.YELLOW  + '　コメディー　　' + colorama.Style.RESET_ALL),
        (401,  colorama.Fore.CYAN    + '　ＶＲゲーム　　' + colorama.Style.RESET_ALL),
        (402,  colorama.Fore.CYAN    + '　　　宇宙　　　' + colorama.Style.RESET_ALL),
        (403,  colorama.Fore.CYAN    + '　　空想科学　　' + colorama.Style.RESET_ALL),
        (404,  colorama.Fore.CYAN    + '　　パニック　　' + colorama.Style.RESET_ALL),
        (9901, colorama.Fore.MAGENTA + '　　　童話　　　' + colorama.Style.RESET_ALL),
        (9902, colorama.Fore.MAGENTA + '　　　詩　　　　' + colorama.Style.RESET_ALL),
        (9903, colorama.Fore.MAGENTA + '　　エッセイ　　' + colorama.Style.RESET_ALL),
        (9904, colorama.Fore.MAGENTA + '　　リプレイ　　' + colorama.Style.RESET_ALL),
        (9999, colorama.Fore.MAGENTA + '　　その他　　　' + colorama.Style.RESET_ALL),
        (9801, colorama.Fore.WHITE   + '　ノンジャンル　' + colorama.Style.RESET_ALL),
    ]
    for p_val, p_name in periods:
        if genre == p_val:
            return p_name
    return periods[0][1]

def convert_date_period(date_str):
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

def parse_data(data):
    j = json.loads(data)
    if j[0]['allcount'] == 0:
        return '[404]'

    last = j[0]['allcount'] + 1
    if last > 501:
        last = 501

    ret = ''
    for i in range(1, last):
        item = j[i]
    
        # color genre and ncode-link
        title = ''
        ncode = ''
        if item.get('nocgenre'):
            ncode = colorama.Fore.YELLOW + '{:7s}'.format(item['ncode'].lower()) + colorama.Style.RESET_ALL
            title = '[' + decode_genre(item['nocgenre']) + ']'
        else:
            ncode = colorama.Fore.CYAN + '{:7s}'.format(item['ncode'].lower()) + colorama.Style.RESET_ALL
            title = '[' + decode_genre(item['genre']) + ']'

        # color title if it is single
        short = ''
        if item['noveltype'] == 1:
            short = colorama.Fore.WHITE
        elif item['noveltype'] == 2:
            short = colorama.Fore.YELLOW
        else:
            short = colorama.Fore.RED

        title += ' ' + short + colorama.Style.BRIGHT + item['title'] + colorama.Style.RESET_ALL + colorama.Style.DIM + ' <' + item['writer'] + '>'  + colorama.Style.RESET_ALL

        # color status if the work is done or continue
        stat = ''
        if item['end'] == 0:
            stat = colorama.Fore.YELLOW + '完結済' + colorama.Style.RESET_ALL
        elif item['end'] == 1:
            stat = colorama.Fore.GREEN + '連載中' + colorama.Style.RESET_ALL
        else:
            stat = 'エラー'

        # calculate when is the last update
        # general_lastup  編集の場合は反映されません
        # novelupdated_at 最後に小説データが更新された時刻
        #last_str = item['general_lastup'] + ' +0900'
        last_str = item['novelupdated_at'] + ' +0900'
    
        ret += ('[{:3d}][{}][{}][{}][{:10,}({:3d})]{}\n'.format(i, ncode, stat, convert_date_period(last_str), item['length'], item['kaiwaritu'], title))
    return ret

def process_item(item):
    if not item.startswith('http'):
        return item + '\n'

    # the server will give EVERYTHING if empty
    if item.endswith('='):
        return '[{0}Format{2}] {0}{1}{2}\n'.format(colorama.Fore.RED, item, colorama.Style.RESET_ALL)

    try:
        data = fetch_data.download(item)
    except:
        return '[{0}Retrive{2}] {0}{1}{2}\n'.format(colorama.Fore.RED, item, colorama.Style.RESET_ALL)

    result = parse_data(data)
    if result == '[404]':
        result = '[{0}Not found{2}] {0}{1}{2}\n'.format(colorama.Fore.RED, item, colorama.Style.RESET_ALL)
    return result

def do_query(query):
    ret = ''
    with multiprocessing.Pool(32) as p:
        r = p.map(process_item, query)
    for s in r:
        ret += s
    return ret

ncode_default = 'api/?of=n-l-w-t-e-gl-nu-nt-ka-g-ng&out=json&lim=500'

r15_uri_g = 'https://api.syosetu.com/novelapi/' + ncode_default
r18_uri_g = 'https://api.syosetu.com/novel18api/' + ncode_default

r15_uri = r15_uri_g + '&ncode='
r18_uri = r18_uri_g + '&ncode='

ncode_re = r'//(?P<type>.*)\.syosetu\.com/(?P<ncode>n[^/]*)/?'

def search_file_remote_order(lines):
    r15 = r15_uri
    r18 = r18_uri
    for l in lines:
        m = re.search(ncode_re, l)
        if m:
            if m.group('type') == 'ncode':
                r15 += m.group('ncode') + '-'
            elif m.group('type') == 'novel18':
                r18 += m.group('ncode') + '-'
    query = ['R15 novel:']
    query.append(r15)
    query.append('R18 novel:')
    query.append(r18)
    return do_query(query)

def search_file_local_order(lines):
    query = []
    for l in lines:
        m = re.search(ncode_re, l)
        if m:
            if m.group('type') == 'ncode':
                query.append(r15_uri + m.group('ncode'))
            elif m.group('type') == 'novel18':
                query.append(r18_uri + m.group('ncode'))
        else:
            query.append(l)
    return do_query(query)


query_global_help = '''
query.py <type> <order>

type:
  t   短編
  r   連載中
  er  完結済連載小説
  re  連載小説
  ter 短編と完結済連載小説

order:
  new           新着更新順
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
  old           更新が古い順
'''

def search_global(type_, order):
    query = ['R15 novel:']
    query.append(r15_uri_g + '&type=' + type_ + '&order=' + order)
    query.append('R18 novel:')
    query.append(r18_uri_g + '&type=' + type_ + '&order=' + order)
    return do_query(query)
