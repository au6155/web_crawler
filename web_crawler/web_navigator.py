from bs4 import BeautifulSoup as bs
from googletrans import Translator
from text_processor import normalize_text
from html_processor import extract_text
import time
import random
import requests


def wait(min, max = 0): # milliseconds to wait
    if min > max: 
        max = min
    time_to_wait = random.randint(min, max) / 1000
    time.sleep(time_to_wait)

def get_google_search_links(google_keyword):

    keywd = google_keyword.replace(' ', '+')
    resp = requests.get('https://www.google.com/search?q=%s&filter=0&start=%d' % (keywd, 1))
    time.sleep(2.5)

    if resp.status_code != 200:
        print('Unable to fetch Google results. Status code %d.Trying again...' % resp.status_code)
        time.sleep(2)
        resp = requests.get('https://www.google.com/search?q=%s&filter=0&start=%d' % (keywd, 1))
            
        if resp.status_code != 200:
            print('Unable to fetch Google results again. Exiting with status code %d' % resp.status_code)
            return []

    time.sleep(1)
    all_the_links_collected = []

    no_of_results_fetched = 0

    while True:
        soup = bs(resp.content, 'lxml')

        links = soup.find_all('div', {'class':'jfp3ef'})

        for link in links:
            try:
                href = link.find('a')['href']
                href = href.replace('/url?q=', '')
                place = href.find('&sa=U&ved=')
                if place != -1:
                    href = href[:place]
                all_the_links_collected.append(href)
            except:
                pass
        # print('links: ', len(all_the_links_collected))

        no_of_results_fetched += len(links)

        try:
             resp = requests.get('https://www.google.com/search?q=%s&filter=0&start=%s' % (keywd, no_of_results_fetched + 1))
        except Exception as e:  
            print(e)
            return all_the_links_collected
            
        if len(links) < 3:
            break

        # adding at least some randomness to simulate human browsing (but this is nowhere near enough)
        time_to_wait = random.randint(200, 350) / 100
        time.sleep(time_to_wait)
        
    return all_the_links_collected

def get_bing_search_links(search):
    main_url = 'https://northeurope.api.cognitive.microsoft.com/bing/v7.0/search' # Bing API URL
    count = 40
    links = []
    for n in range(0, count):
        payload = {'q': search, 'count': 50, 'offset': 50 * n, 'responseFilter': ['Webpages']} # make request query and headers for the API
        headers = {'Ocp-Apim-Subscription-Key': '49965ae339ad41e48b29dc0a0b633f0d'}
        r = requests.get(main_url, params = payload, headers = headers)
        # parse the results
        urls = r.json()
        urls = urls['webPages']
        urls = urls['value']
        for url in urls:
            links.append(url['url'])

        time.sleep(3) # pay respect to servers
    return links


def get_duckduckgo_search_links(google_keyword):

    keywd = google_keyword.replace(' ', '+')
    resp = requests.get('https://www.google.com/search?q=%s&filter=0&start=%d' % (keywd, 1))
    time.sleep(2.5)

    if resp.status_code != 200:
        print('Unable to fetch Google results. Status code %d.Trying again...' % resp.status_code)
        time.sleep(2)
        resp = requests.get('https://www.google.com/search?q=%s&filter=0&start=%d' % (keywd, 1))
            
        if resp.status_code != 200:
            print('Unable to fetch Google results again. Exiting with status code %d' % resp.status_code)
            return []

    time.sleep(1)
    all_the_links_collected = []

    no_of_results_fetched = 0

    while True:
        soup = bs(resp.content, 'lxml')

        links = soup.find_all('div', {'class':'jfp3ef'})

        for link in links:
            try:
                href = link.find('a')['href']
                href = href.replace('/url?q=', '')
                place = href.find('&sa=U&ved=')
                if place != -1:
                    href = href[:place]
                all_the_links_collected.append(href)
            except:
                pass
        # print('links: ', len(all_the_links_collected))

        no_of_results_fetched += len(links)

        try:
             resp = requests.get('https://www.google.com/search?q=%s&filter=0&start=%s' % (keywd, no_of_results_fetched + 1))
        except Exception as e:  
            print(e)
            return all_the_links_collected
            
        if len(links) < 3:
            break

        # adding at least some randomness to simulate human browsing (but this is nowhere near enough)
        time_to_wait = random.randint(200, 350) / 100
        time.sleep(time_to_wait)
        
    return all_the_links_collected


# utilizes firefox reader mode to extract only the important text
def download_article(url):
    resp = requests.get(url, timeout = 10)
    if resp.status_code > 399:
        raise Exception('Unable to fetch page. HTTP status code: %d' % resp.status_code)

    html = resp.content

    text = extract_text(html)
    text = normalize_text(text)
    return text, html


def translate_article(txt_to_translate):
    try:    
        chunks = []

        max_length = 4900

        while len(txt_to_translate) > max_length:
            split_pos = txt_to_translate[:max_length].rfind('\n')
            chunk = txt_to_translate[:split_pos]

            if chunk[0] == ' ': chunk = chunk[1:]
            if chunk[-1] == ' ': chunk = chunk[:-1]

            chunks.append(chunk)
            txt_to_translate = txt_to_translate[split_pos:]

        chunks.append(txt_to_translate) # appending the last bit of text

        translated_text = ''
        for chunk in chunks:
            time.sleep(1.5)
            translator = Translator(service_urls=['translate.google.com', 'translate.google.lt'])
            translation = translator.translate(chunk[10:], dest = 'en')
            translated_text += str(translation.text)

    except Exception as e:
        print('web_navigator.py exception 2: Unable to translate text because: ', e)
        return '.'

    return translated_text

def most_common(lst):
    return max(set(lst), key = lst.count)
