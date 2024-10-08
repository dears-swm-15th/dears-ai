import time
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tqdm import tqdm

from collections import deque

import pyperclip
import json
import pickle

from dotenv import load_dotenv
from pprint import pprint

# DB Connection
load_dotenv()

op = webdriver.ChromeOptions()
chrome_service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service = chrome_service, options=op)

NAVER_ID = str(os.environ.get("NAVER_ID"))
NAVER_PW = str(os.environ.get("NAVER_PW"))
CAFE_URL = str(os.environ.get("CAFE_URL"))
num_counts = 100

driver.get("https://nid.naver.com/nidlogin.login")

try: 
    driver.implicitly_wait(1)

    driver.execute_script("document.getElementsByName('id')[0].value=\'"+ NAVER_ID + "\'")
    driver.execute_script("document.getElementsByName('pw')[0].value=\'"+ NAVER_PW + "\'")
    driver.find_element(by=By.XPATH,value='//*[@id="log.login"]').click()

    time.sleep(1)

except: 
    print("no such element") #예외처리

data = {}

board_dict = {
	"궁금한점 질문답변": "34"
    }

board_keys = list(board_dict.keys())
driver.get(CAFE_URL)

for board in board_keys:

    # 게시판 진입
    board = driver.find_element(By.CSS_SELECTOR, f"#menuLink{board_dict[board]}")
    driver.implicitly_wait(3)
    board.click()

    # iframe으로 전환
    driver.switch_to.frame("cafe_main")
    driver.find_element(By.XPATH, '//*[@id="main-area"]/div[5]/table/tbody/tr[1]/td[1]/div[2]/div/a[1]').click()
    time.sleep(1)

    for i in tqdm(range(1, num_counts)):
        cont_date = "2021"

        try:
            cont_url = driver.find_element(By.XPATH, '//*[@id="spiButton"]').get_attribute('data-url')
            cont_num = cont_url.split("/")[-1]
            cont_date = driver.find_element(By.CLASS_NAME, 'date').text
            cont_author = driver.find_element(By.CLASS_NAME, 'nickname').text
            cont_title = driver.find_element(By.CLASS_NAME, 'title_text').text
            cont_text = driver.find_element(By.CLASS_NAME, 'se-module-text').text
            cont_comments = driver.find_elements(By.CLASS_NAME, 'text_comment')
            
            comments = '\n'.join([comment.text for comment in cont_comments])

            # 게시물 작성 날짜가 2021년 이전일 경우 탐색 중지, 다음 게시판으로 이동
            if cont_date[:4] <= '2020':
                break
            
            # 2020년 이후의 데이터는 data 딕셔너리에 추가
            else:
                data["messages"] = [
                    {
                        "role": "system",
                        "content": "너는 웨딩 관련 정보를 알려주는 Q&A 챗봇이야. 웨딩 커뮤니티 질문 게시판에서 가져온 질문과 응답을 학습해서 답변해줘야 해."
                    },
                    {
                        "role": "user",
                        "content": f"제목: {cont_title}, 본문: {cont_text}"
                    },
                    {
                        "role": "assistant",
                        "content": f"댓글 목록: {comments}"
                    }
                ]


                # data["messages"] = [{"dksd": "dksd"}]

        except:
            pass

        print(f"--------------- {i} 번째 게시물 ---------------")
        print(f"title: {cont_title}")
        print(f"content: {cont_text}")
        print("---------------------------------------------")

        # 다음 게시물로 이동
        try:
            driver.find_element(By.CSS_SELECTOR, "#app > div > div > div.ArticleTopBtns > div.right_area > a.BaseButton.btn_next.BaseButton--skinGray.size_default").click()
        except:
            driver.find_element(By.CSS_SELECTOR, "#app > div > div > div.ArticleTopBtns > div.right_area > a.BaseButton.btn_next.BaseButton--skinGray.size_default > span").click()

        time.sleep(3)


        # 게시물을 탐색할 때마다 JSONL 파일에 데이터 추가 및 저장
        if i % 1 == 0:
            with open("./data.jsonl", 'a', encoding="UTF-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')

