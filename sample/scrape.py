import csv
import os
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse

with open('wearings.csv', 'w') as handle:
    writer = csv.DictWriter(
        handle,
        fieldnames=['date', 'wearer', 'slug', 'name'],
    )
    writer.writeheader()

    for year in range(2012, 2022):
        req = requests.get('http://norm.hasworn.com/%s/' % year)
        soup = BeautifulSoup(req.content, 'html.parser')
        for wearing in soup.select('ul.month li'):
            slug = os.path.basename(wearing.select('a')[0]['href'])
            shirt, when = wearing.select('b')
            date = parse(when.text)
            writer.writerow({
                'date': date.date(),
                'wearer': 'norm',
                'name': shirt.text,
                'slug': slug,
            })
