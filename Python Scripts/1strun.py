import pandas as pd
import requests
from bs4 import BeautifulSoup

# Set up the headers and request the webpage
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'}
webpage = requests.get('https://dealsheaven.in/?page=1', headers=headers).text
soup = BeautifulSoup(webpage, 'lxml')

# Find and extract relevant data from the HTML
company = soup.find_all('div', class_='deatls-inner')
title = []
price = []
Rating = []
website_links = []

for i in company:
    title.append(i.find('h3').text.strip())
    price.append(i.find_all(class_='price')[0].text.strip())
    Rating.append(i.find_all(class_='star')[0].text.strip())
    website_link = i.find('a')['href']
    website_links.append(website_link)

# Create a DataFrame with the extracted data
d = {'title': title, 'price': price, 'Rating': Rating, 'website': website_links}
df = pd.DataFrame(d)

# Save the DataFrame to a CSV file
df.to_csv('deals_information.csv', index=False)
print("Data saved to 'deals_information.csv'")
