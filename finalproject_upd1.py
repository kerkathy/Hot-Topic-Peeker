#final project
"""
Created on Mon Dec 24 12:15:53 2018
"""
from newsapi import NewsApiClient
from selenium import webdriver
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request, urllib.parse, urllib.error
import re
#regular expression
from pytrends.request import TrendReq  # 引入google trends api套件
import json #引入json
import argparse
#匯入標準程式庫 argparsimport requests
import requests
'''from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
'''

######################PART I: find the most discussed topic######################
driver = webdriver.Chrome(executable_path='C:/Users/acer/Desktop/study/Python/chromedriver')
    #open webdriver
driver.get('https://trends.google.com/trends/trendingsearches/daily?geo=TW')
    #go to google trend's site
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
    #use beatiful soup
driver.quit()
print_dict=[]
link_dict=[]
    #這是第一個要印出來的結果(搜尋次數跟結果)
title_dict=[]
temp_dict=[]
    #等等要用來放在kw list裡的搜尋關鍵字
def grabbing(soup):
    #grabs content puts it in a dict
    master_dict=[]
    for x in soup.find_all('div', class_='feed-item contracted-item'):
        #search by CSS class using the keyword argument class_:
        title = re.sub(r'\s+', ' ',x.find(class_='title').text).strip()
        #re.sub(pattern, repl, string, count=0, flags=0)
        #Return the string obtained by replacing the leftmost non-overlapping occurrences of pattern in string by the replacement repl.
        summary = x.find(class_='summary-text').text.strip()
        link = x.findAll('a', href=True)[1]["href"]
        source = x.find(class_='source-and-time').text.strip()
        search_count = x.find(class_='search-count-title').text
        date = x.find_all_previous('div', class_='content-header-title')[0].text
        #從網頁原始碼中找到大意 連結 來源 搜尋次數 日期
        temp_dict = {'Link':link,  'Searches':search_count,'Source':source,'Summary':summary, 'Title':title, 'Date':date}
        prints = {'Searches':search_count,'Title':title,'Date':date}
        title_dict.append(title)
        master_dict.append(temp_dict)
        '''所有資料的dict'''
        print_dict.append(prints)
        '''print_dict: 只有search(次數)跟title(搜尋結果)的表格'''
    return master_dict,title_dict

grabbing(soup)
first_re = pd.DataFrame.from_dict(print_dict)
#轉成panda表格
#first result
#print(master_dict)

print("最近的10個熱搜字詞和搜尋次數:")
print(first_re.head(10))
while True:
    try:
        keynum_str = input("對第幾個關鍵字特別有興趣呢(輸入0-9之間的數字):")
        keynum = int(keynum_str)
        if (keynum > 9):
            print("要輸入0-9的數字! Please try again ...")
            continue
        break
    except ValueError:
        print("要輸入0-9的數字! Please try again ...")
print("您要查的關鍵字是:",title_dict[keynum])

#######################part2:照地區分(pytrend api)######################
pytrend = TrendReq(hl='en-US', tz=360)
pytrend.build_payload(kw_list=[title_dict[keynum]], cat=0, timeframe='now 1-d', geo='TW', gprop='')
#pytrend.build_payload(kw_list=[title_dict[0],title_dict[1],title_dict[2]], cat=0, timeframe='now 1-d', geo='TW', gprop='')
"""kw_list=放入想搜尋的字串，最多5個
cat=類別，要google trends網站看一下你要的類別編號是什麼
timeframe=時間區段 ; geo=地理區域，台灣是TW
gprop=Google property，搜尋結果的類型，有image, news, youtube..."""

# Interest by Region
interest_by_region_df = pytrend.interest_by_region(resolution='DMA')
    #resolution=DMA:以metro為單位搜尋
print("不同地區的熱搜程度(0~100):")
print(interest_by_region_df.head())

while True:
    try:
        condition = input("想根據相關程度(1)或是熱門程度(2)來查找新聞?輸入1或2:")
        if (condition!='1' and condition!='2'):
            print("只能輸入1或2!!")
            continue
        break
    except ValueError:
        print("只能輸入1或2!!")
######################PART3:用News API抓新聞摘要######################################
title = str(title_dict[keynum])
all_article=[]
def news_content(keyw,con):
    if (con=='1'):
        print("===========依據相關程度排序的新聞===============")
        url = ('https://newsapi.org/v2/everything?'
       'q='
       +keyw+
       '&'
       'from=2019-01-10&'
       'sortBy=relevancy&'
       'apiKey=79b54c4dd8ee4e758cd97b9460fe79d8')
    if (con=='2'):
        print("===========依據熱門程度排序的新聞===============")
        url = ('https://newsapi.org/v2/everything?'
       'q='
       +keyw+
       '&'
       'from=2019-01-10&'
       'sortBy=popularity&'
       'apiKey=79b54c4dd8ee4e758cd97b9460fe79d8')
    
    response = requests.get(url)
    all_news_j = response.json()

    body = all_news_j["articles"]
        #從json的{}裡面找標籤為articles的(配合news api)
    for i in range(len(body)):
        #印出每篇新聞摘要
        content = body[i]["description"]
        title = body[i]["title"]
        author = body[i]["author"]
        urll = body[i]["url"]
        print("***第%d篇***" % i)
        print("標題:",title)
        print("內文:",content)
        print("新聞來源:",author)
        print("新聞網址:",urll)
        all_article.append(content)
    return all_article

news_content(title,condition)


"""
######################Part4:開始用NL API 分析文字######################################################

def print_result(article):
    score = article.document_sentiment.score
    magnitude = article.document_sentiment.magnitude
    '''for index, sentence in enumerate(article.sentences):
        sentence_sentiment = sentence.sentiment.score
        print('Sentence {} has a sentiment score of {}'.format(
            index, sentence_sentiment))
        #擷取各個語句的情緒 score 值'''
    print('Overall Sentiment: score of {} with magnitude of {}'.format(score, magnitude))
        #擷取整體評論的情緒 score 值
    return 0

def analyze(article):
    #對 LanguageServiceClient 執行個體呼叫 analyze_sentiment 方法來存取服務
    '''Run a sentiment analysis request on text within a passed filename.'''
    client = language.LanguageServiceClient()

    '''
    我是直接用plain text所以應該不用讀檔案的這段
    with open(article, 'r') as review_file:
        # Instantiates a plain text document.
        content = review_file.read()
    現在content應該是個字串?
    '''
    
    document = types.Document(
        content=article,
        type=enums.Document.Type.PLAIN_TEXT)
    article_a = client.analyze_sentiment(document=document)

    # Print the results
    print_result(article_a)
    
'''
args是命令列引數的寫法 所以我應該不用
parser = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('movie_review_filename',help='The filename of the movie review you\'d like to analyze.')
args = parser.parse_args()
'''
def explicit():
    from google.cloud import storage

    # Explicitly use service account credentials by specifying the private key
    # file.
    storage_client = storage.Client(project='gleaming-medium-225806',credentials=credentials.from_service_account_json('apikey.json'))
   # storage_client = storage.Client.from_service_account_json('service_account.json')
    # Make an authenticated API request
    buckets = list(storage_client.list_buckets())
    print(buckets)

explicit()
for i,element in enumerate(all_article):
    #(p.s.)all_article是裡面很多字串的list
    print("第%d篇摘要分析:" % i)
    analyze(element)
    #分開分析每一篇摘要
    #剖析針對文字檔案名稱所傳遞的引數，並將其傳遞至 analyze() 函式
"""