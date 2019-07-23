#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
웹크롤링으로 이미지 다운 for https://eguru.tumblr.com
"""

from bs4 import BeautifulSoup

# import multiprocessing
import urllib.request
import urllib.parse
import re
import os
import pickle

def get_source_code(url):
    """
    소스코드 가져오기
    """
    with urllib.request.urlopen(url) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')

    return soup


if __name__ == "__main__":

    main_url = "https://eguru.tumblr.com"
    book_nm = "one-piece"    # one-piece / 데스노트 등등
    dst_url = main_url + "/" + urllib.parse.quote_plus(book_nm)

    book_vol_info = list()


    dirPath = book_nm
    if not os.path.exists(dirPath):
        os.mkdir(dirPath)

    if os.path.exists(dirPath + '/' + '[' + book_nm + ']' + ' comicbook_info.pickle'):
        print('파일에서 읽음')
        with open(dirPath + '/' + '[' + book_nm + ']' + ' comicbook_info.pickle', 'rb') as f:
            book_vol_info = pickle.load(f)
    else:
        print('웹 크롤링')
        html_src = get_source_code(dst_url)
        a_tag = html_src.find_all("a", attrs={"target":"_blank"})   # <a> 태그 내역 가져오기

        for i in a_tag:
            a_href, a_text = i['href'], i.text  # <a> 태그의 href 속성 값, text 값
            if '/post/' in a_href:
                book_vol_info.append([a_text, main_url + a_href])

        with open(dirPath + '/' + '[' + book_nm + ']' + ' comicbook_info.pickle', 'wb') as f:
            pickle.dump(book_vol_info, f)


    if not os.path.exists(dirPath + '/' + '[' + book_nm + ']' + ' comicbook_info.txt'):
        with open(dirPath + '/' + '[' + book_nm + ']' + ' comicbook_info.txt', 'w') as f:
            f.writelines('name' + '\t' + 'url' +'\n')
            for i in book_vol_info:
                f.writelines(i[0] + '\t' + i[1] +'\n')
                    

    
    for i in book_vol_info:
        book_vol_nm = i[0]
        book_vol_url = i[1]

        if not os.path.exists(dirPath + '/' + book_vol_nm.replace('/','_') + '/'):

            print('[{}] 페이지 정보 가져오기 시작'.format(book_vol_nm))
            if not os.path.exists(dirPath + '/' + book_vol_nm.replace('/','_') + '/'):
                os.mkdir(dirPath + '/' + book_vol_nm.replace('/','_') + '/')

            book_vol_src = get_source_code(book_vol_url)

            img_tag = book_vol_src.find_all("img", attrs={"alt":"image"}, src=re.compile(r"https.+?.jpg"))

            page_info = list()
            for i in img_tag:
                try:
                    page_url = i['data-orig-src']
                except KeyError as e:
                    print('KeyError : {}'.format(e))
                    try:
                        page_url = i['src']
                    except KeyError as e2:
                        print('KeyError : {}'.format(e2))
                

                regexp = re.compile(r'(?<=\/)[\d\w-]+?\.jpg')
                page_nm = regexp.search(str(page_url)).group()

                print(page_nm, page_url)
                page_info.append([page_nm, page_url])


            if page_info:
                if not os.path.exists(dirPath + '/' + book_vol_nm.replace('/','_') + '/' + '[' + book_vol_nm.replace('/','_') + ']' + ' page_info.txt'):
                    with open(dirPath + '/' + book_vol_nm.replace('/','_') + '/' + '[' + book_vol_nm.replace('/','_') + ']' + ' page_info.txt', 'w') as f:
                        f.writelines('name' + '\t' + 'url' +'\n')
                        for i in page_info:
                            f.writelines(i[0] + '\t' + i[1] +'\n')
                            
