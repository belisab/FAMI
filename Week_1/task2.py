# This file is for the task of extracting news headlines.


import requests
from bs4 import BeautifulSoup
import pandas as pd

# Website url
url = "https://www.helsinki.fi/en/news/news-and-press-releases"

response = requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')
print(soup)




# News headlines are under <hy-general-list


