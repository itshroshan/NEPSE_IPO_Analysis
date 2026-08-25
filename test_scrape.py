import requests
from bs4 import BeautifulSoup
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def test_sebon():
    url = "https://sebon.gov.np/public-issues-data"
    response = requests.get(url, headers=headers, verify=False)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else 'No Title'
        print(f"Page Title: {title}")
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        if tables:
            th_headers = [th.text.strip() for th in tables[0].find_all('th')]
            print(f"  Headers: {th_headers}")
            rows = tables[0].find_all('tr')
            print(f"  Row count: {len(rows)}")
            if len(rows) > 1:
                cols = rows[1].find_all('td')
                print(f"  Row 1: {[c.text.strip() for c in cols]}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    test_sebon()
