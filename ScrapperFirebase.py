
import requests
import re
import firebase_admin

from bs4 import BeautifulSoup
from urllib.parse import unquote
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account.
cred = credentials.Certificate('credentials.json')

app = firebase_admin.initialize_app(cred)

db = firestore.client()


def get_lat_long_from_url(url):
    decoded_url = unquote(url)  # Décodage de l'URL
    match = re.search(r'query=(-?\d+\.\d+),(-?\d+\.\d+)', decoded_url)
    if match:
        latitude = match.group(1)
        longitude = match.group(2)
        return latitude, longitude
    return None, None

def get_all_url():
    page_number = 1
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    while True:
        print(f"Fetching data from page {page_number}...")
        url = f'https://www.bigcitynantes.fr/agenda/liste/page/{page_number}/?hide_subsequent_recurrences=1'
        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            print(f"Error: {r.status_code}")
            break

        soup = BeautifulSoup(r.content, 'html.parser')
        urls = soup.find_all("a", class_="tribe-events-calendar-list__event-title-link tribe-common-anchor-thin")

        if not urls:
            print("Plus aucun URL à récupérer")
            break

        for a in urls:
            href = a.get('href')
            if href:
                doc_ref = db.collection('url').add({'url': href})
                print(f"URL: {href}")
        page_number += 1
#get_all_url()


def get_all_data():
    id = 0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    docs = db.collection("url").stream()

    for doc in docs:
        data = doc.to_dict()
        url = data.get("url")  # récupère la valeur du champ 'url'
        print(f"Fetching data for event at {url}...")
        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            print(f"Error: {r.status_code} for URL: {url}")
            continue

        soup = BeautifulSoup(r.content, 'html.parser')

        titles = soup.find_all("h1", class_="tribe-events-single-event-title")
        tag_divs = soup.find_all("div", class_="event-tags")
        descriptions = soup.find_all("div", class_="tribe-events-single-event-description tribe-events-content")

        location_div = soup.find('div', class_='tribe-events-schedule tribe-clearfix')
        date_div = soup.find('div', class_='tribe-events-schedule tribe-clearfix')

        image_div = soup.find("div", class_="tribe-events-event-image")
        image_src = image_div.find("img").get("src") if image_div else "Aucune image disponible"

        coordonate = soup.find_all('a', href=lambda href: href and 'google.com/maps' in href)
        coordinates = [get_lat_long_from_url(coord.get('href')) for coord in coordonate]

        if location_div:
            location_p = location_div.find('p')
            location = location_p.get_text(strip=True) if location_p else "Localisation non trouvée"
        else:
            location = "Localisation non trouvée"

        if date_div:
            date_h2 = date_div.find('h2')
            dates = re.sub(r'(\D)(\d)', r'\1 \2', date_h2.get_text(strip=True)) if date_h2 else "Date non trouvée"
        else:
            dates = "Date non trouvée"

        if not dates or not titles or not tag_divs or not location or not descriptions:
            print("Plus aucune information trouvée.")
            continue

        for title, tag_div, description in zip(titles, tag_divs, descriptions):
            id += 1
            spans = tag_div.find_all("span")
            tags = [' '.join(span.stripped_strings) for span in spans]

            latitude, longitude = coordinates[0] if coordinates and coordinates[0] else (None, None)

            event = {
                "id": id,
                "date": " ".join(dates.strip().split()),
                "title": ' '.join(title.stripped_strings),
                "tags": tags,
                "location": location,
                "descriptions": ' '.join(description.stripped_strings),
                "image": image_src,
                "latitude": latitude,
                "longitude": longitude
            }


            print(f"Id : {id}")
            print(f"Date : {event['date']}")
            print(f"Titre : {event['title']}")
            print(f"Tags : {event['tags']}")
            print(f"Location : {event['location']}")
            print(f"Description : {event['descriptions']}")
            print(f"Image : {event['image']}")
            print(f"Latitude : {event['latitude']}")
            print(f"Longitude : {event['longitude']}")
            print("-" * 40)

            docs = db.collection('evenements').add(event)
get_all_data()
