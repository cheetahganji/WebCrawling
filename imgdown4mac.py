#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
웹크롤링으로 이미지 다운
특정 사이트를 기준으로 웹크롤링을 하기 때문에 다른 사이트 용으로 변경하기 위해선 해당 사이트 소스를 분석해서 적용해야함
"""

from bs4 import BeautifulSoup

import multiprocessing
import urllib.request
import urllib.parse
import re
import json
import os


def get_source_code(url, tag_nm):
    """
    소스코드에서 특정 tag 데이터 가져오기
    """

    with urllib.request.urlopen(url) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        # soup.prettify()
        rst_script = soup.find_all(tag_nm)

    return rst_script




def get_book_volume_info(url, book_nm, tag_nm):
    rst = list()

    dst_url = url + urllib.parse.quote_plus(book_nm)
    html_script = get_source_code(dst_url, tag_nm)

    regexp = re.compile(r'<a href="/post.+?" target="_blank">데스노트.+?</a>')   # 각 권의 정보를 가져오는 정규식
    p = regexp.findall(str(html_script))

    for idx, data in enumerate(p):
        # print('[{}]  : {}'.format(idx, data))
        regexp = re.compile(r'post/.+?(?=" target)')   
        vol_url = regexp.search(str(data)).group()  # 각 권의 url

        regexp = re.compile(book_nm + '.+?(?=</a)')
        vol_nm = regexp.search(str(data)).group()  # 각 권의 이름

        rst.append([main_url + vol_url, vol_nm])
        
    return  rst



def get_page_info(url, tag_nm):
    rst = list()

    dst_url = url
    html_script = get_source_code(dst_url, tag_nm)
    
    #print(html_script)
    # <img src="https://4.bp.blogspot.com/-ODATRzTb3WI/Wo8kbZxeaKI/AAAAAAAA36g/JeUAH9DTa08-gkE4qm8l2iTClvhiPRRAwCKgBGAs/s1600/1-003.jpg" alt="image">

    regexp = re.compile(r'https://\d+.bp.blogspot.com/.+?jpg')   # 각 페이지의 정보를 가져오는 정규식
    p = regexp.findall(str(html_script))

    for idx, page_url in enumerate(p):
        # print('[{}]  : {}'.format(idx, page_url))
        regexp = re.compile(r'[\d\w]+?-\d+\.jpg')   
        page_nm = regexp.search(str(page_url)).group()  # 각 페이지의 파일이름

        rst.append([page_url, page_nm])
        
    return  rst


def save_img(page_info):
    """
    page_info(이미지 url과 경로에 관한 정보를 담은 리스트)를 이용하여 이미지를 특정 위치에 저장한다. 
    """
    page_url = page_info[0]
    page_nm = page_info[1]
    vol_nm = page_info[2]       # 각 권 이름
    dst_path = page_info[3]

    if not os.path.exists(dst_path):        # 해당 파일이 존재하지 않을때만 저장
        urllib.request.urlretrieve(page_url, dst_path)


if __name__ == "__main__":

    pool = multiprocessing.Pool(processes=4)    # 멀티프로세싱을 위해 선언

    main_url = "https://eguru.tumblr.com/"
    book_nm = "데스노트"


    base_path = '/Users/chex2tah/Downloads/' + book_nm 
    if not os.path.isdir(base_path):
        os.mkdir(base_path)

    # main_url에서 각 권의 정보를 가져온다.
    bvi = get_book_volume_info(main_url, book_nm, "a")


    all_info = list()

    # 각 권의 정보에대해 각 페이지의 정보를 가져온다.
    for i in bvi:
        print(i)
        vol_url, vol_nm = i[0], i[1]
        tmp = ['데스노트 ' + str(x) + '권' for x in range(11,12)]
        
        vol_nm = str(vol_nm).replace('/','')

        # 저장될 위치(권) 디렉토리 생성
        if not os.path.isdir(base_path + '/' + vol_nm):
            print(vol_nm)
            os.mkdir(base_path + '/' + vol_nm)

            pi = get_page_info(vol_url, 'img')  # 페이지 정보 가져오기

            for j in pi:
                page_url, page_nm = j[0], j[1]
                j.append(vol_nm)
                j.append(base_path + '/' + vol_nm + '/' + page_nm)
                all_info.append(j)
        
    pool.map(save_img, all_info)
    pool.close()
