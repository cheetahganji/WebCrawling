#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
웹크롤링 이미지 다운(https://eguru.tumblr.com 용)
특정 사이트를 기준으로 웹크롤링을 하기 때문에 다른 사이트 용으로 변경하기 위해선 해당 사이트 소스를 분석해서 적용해야함
"""

from bs4 import BeautifulSoup

import multiprocessing
import urllib.request
import urllib.parse
import re
import os
import pickle
import copy


def get_htlm(url):
    """
    """
    with urllib.request.urlopen(url) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        soup.prettify()

    return soup

def save_data_info(path, filename, content):
    '''
        정보 저장
        파이썬 객체 형태로도 저장하고, 사람이 읽기 쉬운 형태로도 저장
    '''
    if path and filename and content:
        if not os.path.exists(path):
            os.mkdir(path)

        if not os.path.exists(path + '/' + filename + '.pickle'):
            with open(path + '/' + filename + '.pickle', 'wb') as f:
                pickle.dump(content, f)

        if not os.path.exists(path + '/' + filename + '.txt'):
            with open(path + '/' + filename + '.txt', 'w') as f:
                for c in content:
                    f.writelines(c[0] + '\t' + c[1] + '\n')


def get_data_info(path, filename):
    '''
        저장된 파이썬 객체 가져오기
    '''
    content = list()
    full_path = path + '/' + filename + '.pickle'

    if os.path.exists(full_path):
        with open(full_path, 'rb') as f:
            content = pickle.load(f)

    return content


def save_img(page_info):
    """
    page_info(이미지 url과 경로에 관한 정보를 담은 리스트)를 이용하여 이미지를 특정 위치에 저장한다. 
    params:
        page_info : 특정 페이지의 파일이름, url 주소 및 저장될 위치를 갖는 리스트
    """
    page_nm = page_info[0]
    page_url = page_info[1]
    path = page_info[2]

    full_path = path + '/' + page_nm
    
    if not os.path.exists(full_path):        # 해당 파일이 존재하지 않을때만 저장
        urllib.request.urlretrieve(page_url, full_path)
        print('    ', full_path, 'Saved')
    else:
        print('    ', full_path, 'Already Existed')
    
    

if __name__ == "__main__":
    base_url, comicbook_nm = "https://eguru.tumblr.com", "one-piece" 
    dst_url = base_url + "/" + urllib.parse.quote_plus(comicbook_nm)

    path = "/Users/chex2tah/Downloads/" + comicbook_nm
    filename = comicbook_nm + ' info'

    vol_info = list()
    if not os.path.exists(path + '/' + filename + '.pickle'):
        soup = get_htlm(dst_url)
        a_tag_list = soup.select('.body-text p a[target="_blank"]') # 분석해서 가져온 a태그 리스트
        
        for i in a_tag_list:
            vol_nm, vol_url = i.text.replace('/','_'), i['href']    # 책 낱권의 이름, 정보(url)
            vol_info.append([vol_nm, base_url + vol_url])

        save_data_info(path, filename, vol_info)
    else:
        vol_info = get_data_info(path, filename)

    
    pool = multiprocessing.Pool(processes=4)    # 멀티프로세싱을 위해 선언

    for v in vol_info:
        vol_nm, vol_url = v[0], v[1]    # 책 낱권의 이름, 정보(url)
        vol_soup = get_htlm(vol_url)

        img_tag_list = vol_soup.select('.body-text img[alt="image"]') # 분석해서 가져온 img태그 리스트

        page_info = list()
        for i in img_tag_list:
            try:
                page_img, page_img_nm = i['data-orig-src'], ''
            except KeyError as e:
                print('KeyError : {}'.format(e))
                try:
                    page_img, page_img_nm = i['src'], ''
                except KeyError as e2:
                    print('KeyError : {}'.format(e2))

            rst = re.search(r'(?<=\/)[\d\w-]+\.jpg', page_img)
            if rst:
                page_img_nm = rst.group()

            page_info.append([page_img_nm, page_img, path + '/' + vol_nm])

        
        if not os.path.exists(path + '/' + vol_nm):
            os.mkdir(path + '/' + vol_nm)

        print(vol_nm, '저장 시작!')
        pool.map(save_img, page_info)
        print(vol_nm, '저장 완료!\n')

        # break   # 1권만 가져오도록 break 처리

    pool.close()
    
