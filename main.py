from urllib.parse import urlparse
from flask import Flask, request
from flask_restful import Resource, Api
import json
import requests
import re
from bs4 import BeautifulSoup
app = Flask(__name__)
# creating an API object
api = Api(app)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}

categories = ["anime", "hanh-dong", "hai-huoc", "tinh-cam", "harem", "bi-an", "bi-kich", "gia-tuong",
              "hoc-duong", "doi-thuong", "tham-tu", "lich-su", "sieu-nang-luc", "shounen", "shounen-ai",
              "shoujo", "shoujo-ai", "the-thao", "am-nhac", "psychological", "mecha", "quan-doi", "drama",
              "seinen", "sieu-nhien", "phieu-luu", "kinh-di", "ma-ca-rong", "tokusatsu", "tien-hiep", "kiem-hiep", "xuyen-khong",
              "trung-sinh", "huyen-ao", "cna-ngon-tinh", "di-gioi", "cna-hai-huoc", "dam-my", "vo-hiep", "ecchi", "demon", "live-action"]

def bsString(s):
    return s.replace('  ', '').replace('\n', '')


@app.route('/')
def hello():
    return 'hello'


@app.route('/home', methods=['GET'])
def home():
    url = "https://animehay.pro"


@app.route('/search', methods=['GET'])
def search():
    name = request.args.get('name')
    page = request.args.get('page') or 1
    url = "https://animehay.pro/tim-kiem/{}/trang-{}.html".format(name, page)
    my_request = requests.get(url)
    soup = BeautifulSoup(my_request.text, 'html.parser')
    data = getAnimesData(soup)
    if (data):
        return getAnimesData(soup)
    else:
        return "{}"


@app.route('/find/<string:anime_name>', methods=['GET'])
def dataAnime(anime_name):
    url = "https://animehay.pro/thong-tin-phim/{}.html".format(anime_name)
    anime_infor = dict()
    my_request = requests.get(url)
    soup = BeautifulSoup(my_request.content, 'html.parser')

    anime_infor["name"] = soup.find('h1', class_='heading_movie').text
    anime_infor["thumbnail"] = soup.select_one('.first > img').get('src')
    anime_infor["description"] = bsString(
        soup.select_one('.desc').text.replace('Nội dung', ''))

    category = soup.select('.list_cate a')
    a_category = []

    for cate in category:
        a_category.append(bsString(cate.text))

    anime_infor["category"] = a_category
    anime_infor["status"] = bsString(
        soup.find('div', class_="status").text.replace('Trạng thái', ''))
    anime_infor["score"] = bsString(
        soup.find('div', class_="score").text.replace('Điểm', ''))
    anime_infor["duration"] = bsString(
        soup.find('div', class_="duration").text.replace('Thời lượng', ''))

    list_bind = soup.select_one('.bind_movie .scroll-bar')
    if (list_bind):
        a_bind = []
        for bind in list_bind.findAll('a'):
            a_bind.append({"bind_name": bsString(bind.text), "bind_link": '/find/' +
                          bind.get('href').split('/')[-1].replace('.html', '')})
        anime_infor["bind_list"] = a_bind
    else:
        anime_infor['bind_list'] = None
    list_esp = soup.select('.list-item-episode a')
    a_esp = []
    for esp in list_esp:
        a_esp.append({"esp": bsString(esp.text), "esp_link": "/watch/{}".format(
            esp.get('href').split('/')[-1].replace('.html', ''))})
    anime_infor["esp_list"] = a_esp

    return anime_infor
# ---------------------------------------------------------------------------------


@app.route('/watch/<string:anime_name>', methods=['GET'])
def watch(anime_name):
    url = "https://animehay.pro/xem-phim/{}.html".format(anime_name)
    anime_data = dict()
    my_request = requests.get(url)
    soup = BeautifulSoup(my_request.text, 'html.parser')
    # get link video
    script_text = soup.find_all("script", string=True)[5].text
    infor_play_video = re.findall(r"(\{[^{}]+\})", script_text)[0]
    # json decode the object
    infor_play_video = json.loads(infor_play_video)['file']

    anime_data["source"] = infor_play_video
    anime_data["title"] = soup.find('title').text.replace('|| AnimeHay', '')
    anime_data["meta_content"] = soup.find('meta').get('content')
    list_esp = soup.select('.list-item-episode a')
    a_esp = []
    for esp in list_esp:
        a_esp.append({"esp": bsString(esp.text), "esp_link": "/watch/{}".format(
            esp.get('href').split('/')[-1].replace('.html', ''))})
    anime_data["esp_list"] = a_esp
    print(soup)
    return anime_data


@app.route('/<string:cate>/<string:anime_page>', methods=['GET'])
def anime(cate, anime_page):
    print(cate)
    if cate in categories:
        anime_cate = categories.index(cate)+1

        url = "https://animehay.pro/the-loai/anime-{}/{}.html".format(
            anime_cate, anime_page)

        my_request = requests.get(url)
        soup = BeautifulSoup(my_request.text, 'html.parser')
        # get tung data
        return getAnimesData(soup)
    else:
        return {"data":[]}


def getAnimesData(soup):
    animes_data_list = []
    for film in soup.findAll('div', class_='movie-item'):
        if (film):
            anime_data = {}

            anime_data["link"] = "/find/" + \
                film.find('a').get('href').split('/')[-1].replace('.html', '')
            anime_data["name"] = bsString(film.find(
                'div', class_='name-movie').text)
            anime_data["thumbnail"] = film.find(
                'img').get('src')
            anime_data["score"] = bsString(
                film.find('div', class_='score').text)
            anime_data["update"] = film.find(
                'div', class_='episode-latest').text
            animes_data_list.append(anime_data)
    return {'data': animes_data_list}


# driver function
if __name__ == '__main__':

    app.run(debug=True)
