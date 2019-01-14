#!/usr/bin/env python3

from bs4 import BeautifulSoup
import fetch_data
import re

def get_bookmark(data_list):
	uri_list = []
	for d in data_list:
		html = d.decode('utf8', 'ignore')
		soup = BeautifulSoup(html, 'lxml')
		bm = soup.select('div#novellist > ul > li.title > a, div.novellist > ul > li.title > a')
		for b in bm:
			uri_list.append(b['href'])
	return uri_list

# [(uri, data), (uri, data), ...]
def get_minor(data_list):
	uri_list = []
	for pair in data_list:
		html = pair[1].decode('utf8', 'ignore')
		soup = BeautifulSoup(html, 'lxml')
		bm = soup.select('div#novellist, div.novellist')
		#print(soup)
		if len(bm) <= 0:
			continue
		size = 1
		page = soup.select('div.pager_kazu')
		if len(page) > 0:
			m = re.search(r'(?P<total>\d*)ページ中(?P<curr>\d*)ページ目', page[0].get_text())
			if m:
				size = int(m.group('total'))
		for i in range(1, size+1):
			uri_list.append(pair[0] + '&p=' + str(i))
	#print(uri_list)
	return fetch_data.bulk_down(uri_list)

def get_major(uri):
	uri_list = []
	for i in range(1,11):
		uri_list.append(uri + '?nowcategory=' + str(i))
	return fetch_data.bulk_down_with_label(uri_list)

def parse(uri):
	major_list = get_major(uri);
	minor_list = get_minor(major_list);
	return get_bookmark(minor_list)

def r15(uid):
	return parse('https://mypage.syosetu.com/mypagefavnovelmain/list/userid/' + str(uid) + '/')

def r18(xid):
	return parse('https://xmypage.syosetu.com/mypagefavnovelmain18/list/xid/' + str(xid) + '/')

