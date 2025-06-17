import requests
from bs4 import BeautifulSoup
url = 'https://www.omgtu.ru/'
page = requests.get(url)
spisok = []
soup = BeautifulSoup(page.text, "lxml")
spisok = soup.find_all("h3", class_="news-card__title")
for t in spisok:
    print(t.text)
t = [s.get_text(strip=True) for s in spisok]
with open('omgtu_news.txt', 'w') as file:
    for titles in t:
        file.write(titles + '\n')