#!/usr/bin/env python3

import requests
import retry_decorator
import multiprocessing
import tqdm

@retry_decorator.retry(requests.RequestException, tries = 16, delay = 1, backoff = 2)
def download_with_label(uri):
	cookies = dict(over18='yes')
	r = requests.get(uri, cookies=cookies, stream=True)
	r.encoding = 'utf8'
	return (uri, r.text.encode('utf8'))

def download(uri):
	return download_with_label(uri)[1]

def bulk_down_with_label(uri_list):
	with multiprocessing.Pool(8) as p:
		r = list(tqdm.tqdm(p.imap(download_with_label, uri_list), total=len(uri_list)))
	return r

def bulk_down(uri_list):
	with multiprocessing.Pool(8) as p:
		r = list(tqdm.tqdm(p.imap(download, uri_list), total=len(uri_list)))
	return r
