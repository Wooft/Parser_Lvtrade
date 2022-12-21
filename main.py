import requests
import bs4

url = 'https://lvtrade.ru/'
response = requests.get(url)
text = response.text
print(text)



