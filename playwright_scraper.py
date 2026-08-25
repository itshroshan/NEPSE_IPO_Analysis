from playwright.sync_api import sync_playwright

def scrape_sharesansar():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://nepsealpha.com/investment-calendar/ipo", timeout=60000)
        
        page.wait_for_selector("table", timeout=10000)
        print("Table found on Nepse Alpha.")
        
        tables = page.query_selector_all("table")
        for i, table in enumerate(tables):
            headers = table.query_selector_all("th")
            header_texts = [h.inner_text().strip() for h in headers if h.inner_text().strip()]
            print(f"Table {i} headers: {header_texts}")
            
            # Print first 5 rows
            rows = table.query_selector_all("tbody tr")
            print(f"Total rows: {len(rows)}")
            for j in range(min(5, len(rows))):
                cols = rows[j].query_selector_all("td")
                col_texts = [c.inner_text().strip() for c in cols]
                print(f"Row {j}: {col_texts}")

        browser.close()

if __name__ == "__main__":
    scrape_sharesansar()
