def bsString(s):
    return s.replace('  ', '').replace('\n', '')

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
