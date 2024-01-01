import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv, re, json, time


def export_to_json(products: list):
    with open('sample.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)


def export_to_csv(products: list):
    field_names = ['Name', 'Address', 'Description', 'Website']
    with open('sample.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(products)


def get_html(url: str):
    header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'}
    response = requests.get(url, headers=header)

    soup = BeautifulSoup(response.content, 'lxml')

    return soup



def extract_info(html, tag, attribute):
    try:
        return html.find(tag, attribute)['href']
    except KeyError:
        return html.find(tag, attribute).text.strip()
    except TypeError:
        return None



def parse_page(soup):
    content = soup.find('ul', {'searchgroup': '7E92B52E-exhibitors'})
    
    exhibits = content.find_all('h2', {'class': 'm-exhibitors-list__items__item__header__title'})

    for exhibit in exhibits:
        single = exhibit.find('a')['href']
        name = exhibit.find('a').text

        base_url = urljoin('https://london.vetshow.com/', single)

        exhibit_soup = get_html(base_url)

        address = extract_info(exhibit_soup, 'div', {'class': 'm-exhibitor-entry__item__body__contacts__address'}).replace('Address', '')

        # remove whitespaces, tabs, newlines, carriage returns
        cleaned_address = re.sub(r'\s+', ' ', address).strip()

        description = extract_info(exhibit_soup, 'div', {'class': 'm-exhibitor-entry__item__body__description'})
        website = extract_info(exhibit_soup, 'a', {'class': 'p-button p-button--primary'})

        exhibit_details = {
            'Name': name,
            'Address': cleaned_address,
            'Description': description,
            'Website': website
        }

        # to create iterable
        yield exhibit_details


def main():
    all_exhibits = []
    for x in range(1,41):
        print(f'Getting exhibition info from page {x}...')

        url = f'https://london.vetshow.com/exhibitor-list?&page={x}&searchgroup=7E92B52E-exhibitors'
    
        soup = get_html(url)

        exhibit_data = parse_page(soup)
    
        for data in exhibit_data:
            all_exhibits.append(data)
        
            time.sleep(1)
    
    export_to_json(all_exhibits)
    export_to_csv(all_exhibits)

    print('All done')


if __name__ == '__main__':
    main()
