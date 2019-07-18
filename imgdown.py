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


def get_source_code(web_url, tag_nm):
    """
    소스코드에서 특정 tag 데이터 가져오기
    """

    with urllib.request.urlopen(web_url) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        # soup.prettify()
        rst = soup.find_all(tag_nm)

    return rst


def get_book_info(web_url, tag_nm, book_name):
    """
    각 책의 정보를 가져온다.
    """
    book_info = list()

    ls_sc = get_source_code(web_url, tag_nm)      # 태그에 해당되는 소스코드 여러개가 리턴된다(리스트).

    regexp = re.compile(r'{"pageId.+?title.+?pageUriSEO.+?pageJsonFileName.+?"}')   # 각 권의 정보를 가져오는 정규식
    rst = regexp.findall(str(ls_sc))
    

    for item in rst:
        json_item = json.loads(item)

        if book_name in item:
            book_info.append([json_item['title'], web_url + json_item['pageUriSEO']])

    book_info = sorted(book_info)

    return book_info


def get_page_info(book_info, tag_nm):
    """
    각 페이지의 정보를 가져온다.
    """
    book_no = book_info[0]
    book_url = book_info[1]

    ls_sc = get_source_code(book_url, tag_nm)      # 태그에 해당되는 소스코드 여러개가 리턴된다(리스트).

    regexp = re.compile(r'"title":"\d{10}.+?"uri":".+?"')   # 해당 권의 페이지 정보를 가져오는 정규식
    rst = regexp.findall(str(ls_sc))
    
    page_info = list()
    for item in rst:
        json_item = json.loads('{' + item + '}')
        page_info.append([book_no, json_item['title'], 'https://static.wixstatic.com/media/' + json_item['uri']])

    page_info = sorted(page_info)

    return page_info


def save_img(page_info):
    """
    page_info(이미지 url과 경로에 관한 정보를 담은 리스트)를 이용하여 이미지를 특정 위치에 저장한다. 
    """
    book_no = page_info[0]
    img_name = page_info[1]
    img_url = page_info[2]
    base_path = page_info[3]

    dst_path = base_path + book_no + '/' + img_name

    print(img_url)

    #urllib.request.urlretrieve(img_url, dst_path)


if __name__ == "__main__":

    pool = multiprocessing.Pool(processes=4)    # 멀티프로세싱을 위해 선언

    web_url = 'https://manabogo3.wixsite.com/mana/'
    tag_nm = 'script'

    book_name = '슬램덩크'
    base_path = 'C:/Users/wykim/Desktop/' + book_name + '/'
    
    book_info = get_book_info(web_url, tag_nm, book_name)
    

    for bi in book_info:
        bi[0] = bi[0]

        if bi[0] == '슬램덩크 12권':    # 권 수가 많은 경우 van될까봐 1권 씩...

            # 저장될 위치 디렉토리 생성
            if not os.path.isdir(base_path):
                os.mkdir(base_path)
                if not os.path.isdir(base_path + bi[0]):
                    os.mkdir(base_path + bi[0])
            else:
                if not os.path.isdir(base_path + bi[0]):
                    os.mkdir(base_path + bi[0])

            page_info = get_page_info(bi, tag_nm)

            for pi in page_info:
                pi.append(base_path)

            pool.map(save_img, page_info)
            
            print(bi[0] + ' 저장 완료!')

    pool.close()
