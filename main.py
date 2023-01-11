import pprint
import re
import requests
import bs4

url = 'https://lvtrade.ru'

def getCategories(url):
    url_catalogs = '/catalog/zapchasti/'
    fullurl = url + url_catalogs
    text = requests.get(fullurl).text
    datasoup = bs4.BeautifulSoup(text, features="html.parser")
    categories = datasoup.find_all(class_='section-compact-list__image flexbox flexbox--row')
    links = []
    for category in categories:
        for item in category.find_all('a'):
            data = (item.contents[0].get('title'), item.get('href'))
            links.append(data)
    getNumbers(datasoup)
    return links

def getNumbers(datasoup):
    countes = datasoup.find_all(class_="element-count2 muted font_upper")
    pattern = re.compile("[0-9]+")
    num = 0
    for count in countes:
        result = pattern.findall(count.text)
        num += int(result[0])
    print(f'Количество запчастей на сайте: {num}')
    return count

def getPrices():
    list_links = getCategories(url)
    for item in list_links:
        link = url + item[1]
        text = requests.get(link).text
        soup = bs4.BeautifulSoup(text, features='html.parser')
        parts = soup.find_all(class_='item_info')
        print(parts)
        for part in parts:
            pattern_article = re.compile('[0-9]+')
            pattern_name = re.compile('\s[а-яёА-ЯЁA-Z0-9]+')
            article = pattern_article.findall(part.contents[1].contents[3].text)
            name = pattern_name.findall(part.contents[1].contents[3].text)
            price = pattern_article.findall(part.contents[3].contents[1].text)
            print()

if __name__ == "__main__":
    print(getPrices())
