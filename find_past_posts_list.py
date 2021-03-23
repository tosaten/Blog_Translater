from bs4 import BeautifulSoup
import requests
import pickle

new_posts_url_list = []

site = requests.get("https://readwrite.com/")
soup = BeautifulSoup(site.text,'html.parser')

#postsに最新投稿のデータを格納
posts = soup.find(class_="home-posts-wrap").find_all('article')

for x in posts:
    new_posts_url = x.find('div',class_ = "col-md-3 post-thumb").find('a').get('href')
    new_posts_url_list.append(new_posts_url)

#次使うために、テキストファイルにリストを出力
f = open('./befor_posts.pickle', 'wb')
pickle.dump(new_posts_url_list, f)
f.close()
