import requests
from bs4 import BeautifulSoup
import datetime
import json
from selenium import webdriver
import time
import pyperclip
import schedule
import datetime

webhook_url = "https://discord.com/api/webhooks/820751498962534463/bqrTFSAAO5PD9pUr1Y5Yps3ZO-kX8KWYQ0KvJk6WpLpBc86JQoJFbr9iP_DxrnD5LeCw"

def new_posts_send_discord(webhook_url):
    try_count = 0
    #--------最新記事のスクレイピング--------

    site = requests.get("https://readwrite.com/")
    soup = BeautifulSoup(site.text,'html.parser')

    #postsに最新投稿のデータを格納
    posts = soup.find(class_="home-posts-wrap").find_all('article')

    #空リストの作成
    articles = []
    new_posts_url_list = []

    try_count = 0
    if try_count == 0:
        befor_posts = [] #１度目の試行のみ
        try_count += 1
    else:
        pass

    # 前回と今回のスクレイピング結果を比較して、新しいものだけリストで返す
    def search_post(posts, befor_posts):
        for post in posts:
            #前回取得したリストに入ってない投稿があれば
            if post not in befor_posts:
                #articlesに格納
                articles.append(post)
        return articles

    new_posts = search_post(posts, befor_posts)
    for x in new_posts:
        new_posts_url = x.find('div',class_ = "col-md-3 post-thumb").find('a').get('href')
        new_posts_url_list.append(new_posts_url)

    befor_posts = new_posts_url_list

    #--------取得した最新記事を投稿できる形に変換--------
    #もし最新記事があったら
    if len(new_posts_url_list) >= 1:

        print(str(len(new_posts_url_list)) + "件の最新記事を見つけました")

        for url in new_posts_url_list:

            site = requests.get(url)
            soup = BeautifulSoup(site.text,'html.parser')
            [tag.extract() for tag in soup(string='n')]

            #記事のタイトルの取得
            title = soup.find('h1').text

            #記事の文章の取得
            a = soup.find('div', class_ = 'entry-content col-md-10')
            body_list = []

            #コンテンツがインデックスエラーを起こすまで試行
            #もしそのリストのタグが規定のものであれば，body_listに格納
            stop = 0
            n = 0
            back_h3 = "\n\n**"
            front_h3 = "**\n"

            #取得した本文を本文リストに追加
            while stop <= 1:
                try:
                    #<div>タグが現れたらストップ
                    if a.contents[n].name == 'div':
                        stop += 1
                    #見出しタグが現れたら，改行と太字にする
                    elif a.contents[n].name == 'h3':
                        b = a.contents[n].text
                        body_list.append(back_h3)
                        body_list.append(b)
                        body_list.append(front_h3)
                    else:
                        b = a.contents[n].text
                        body_list.append(b)
                except AttributeError:
                    pass
                n += 1

            #-----------selenium操作-----------
            
            transfer_body_list = []

            #ChromeDriverのパスを引数に指定しChromeを起動
            driver = webdriver.Chrome("../blog/chromedriver.exe")
            #指定したURLに遷移する
            driver.get("https://www.deepl.com/ja/translator")
            time.sleep(3)

            #検索テキストボックスの要素をId属性名から取得
            text_box = driver.find_element_by_xpath("/html/body/div[2]/div[1]/div[5]/div[2]/div[1]/div[2]/div/textarea")
            input_selector = driver.find_element_by_css_selector("#dl_translator > div.lmt__text > div.lmt__sides_container > div.lmt__side_container.lmt__side_container--target > div.lmt__textarea_container > div.lmt__target_toolbar.lmt__target_toolbar--visible > div.lmt__target_toolbar__copy > button")
            #output_box = element.find_element_by_xpath('/html/body/div[2]/div[1]/div[5]/div[2]/div[3]/div[3]/div[6]/div[2]/button')

            #検索テキストボックスに文字列を入力
            text_box.send_keys(title)
            #翻訳されるまで待つ
            time.sleep(5)
            #クリップボックスに出力をコピー
            input_selector.click()
            time.sleep(1)
            #クリップボードから翻訳した文字列を変数に格納
            transfer_title = pyperclip.paste()

            text_box.clear()

            for befor_body_list in body_list:
                #検索テキストボックスに文字列を入力
                text_box.send_keys(befor_body_list)
                #翻訳されるまで待つ
                time.sleep(3)

                # this scrolls untill the element is in the middle of the page
                element = input_selector
                desired_y = (element.size['height'] / 2) + element.location['y']
                current_y = (driver.execute_script('return window.innerHeight') / 2) + driver.execute_script ('return window.pageYOffset')
                scroll_y_by = desired_y - current_y
                driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_y_by)
                
                time.sleep(2)
                
                input_selector.click()

                time.sleep(0.5)
                #クリップボードから翻訳した文字列を変数に格納
                paste_str = pyperclip.paste()
                transfer_body_list.append(paste_str)
                
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                text_box.clear()

            driver.quit()

            send_message = ' '.join(transfer_body_list)
            send_message = send_message[:1500]

            send_message = "**" + transfer_title + "**\n\n" + "URL:" + url + "\n\n" + send_message + "[...]"

            main_content = {'content': send_message}
            headers      = {'Content-Type': 'application/json'}

            response     = requests.post(webhook_url, json.dumps(main_content), headers=headers)
    #なかったら
    else:
        print('最新記事はありませんでした')


def job():
    print("===============================")
    print(datetime.datetime.now())
    print("START PERIODIC EXECUTION")
    new_posts_send_discord(webhook_url)
    print("===============================")+
schedule.every().minute.do(job)

while True:
    schedule.run_pending()
    time.sleep(30)