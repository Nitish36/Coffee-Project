"""from playwright.sync_api import sync_playwright
def scrape_quote(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto('https://playwright.dev/python/docs/test-assertions')
    quotes = page.locator('tbody').all_text_contents()
    for quote in quotes:
        print(quote)

with sync_playwright() as playwright:
    scrape_quote(playwright)"""

l = [10,"ABC",10.5,99,"DEF",10]

thislist = ["apple", "banana", "cherry"]
tropical = ["mango", "pineapple", "papaya"]
thislist.extend(tropical)
print(thislist)

thislist.remove("cherry")
print(thislist)
thislist.pop(3)
print(thislist)

del thislist[0]
print(thislist)

del thislist
print(thislist)

