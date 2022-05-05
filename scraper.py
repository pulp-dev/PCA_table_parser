import requests
from selenium import webdriver
from lxml.html import fromstring
from bs4 import BeautifulSoup as bs


# parser class
class Scraper:
    def __init__(self):
        self.url = 'https://oto-register.autoins.ru/pto/'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 "
                          "Safari/537.36 "
        }
        self.driver_path = r'./geckodriver/geckodriver.exe'

        # selenium driver
        self.options = webdriver.FirefoxOptions()
        self.options.add_argument("--start-maximized")
        self.driver = webdriver.Firefox(executable_path=self.driver_path, options=self.options)

        # page
        self.current_page = 1

        # result
        self.info = {}

    # go for next page
    def next_page(self):
        buttons = self.driver.find_elements_by_xpath("//a[@class='ui-commandlink ui-widget']")
        for el in buttons:
            if el.text == str(self.current_page + 1):
                el.click()
                return

    def get_info_from_elements_page(self, elements_url):
        r = requests.get(elements_url, headers=self.headers)
        dom = fromstring(bytes(bytearray(r.text, encoding='utf-8')))
        phone_number = dom.xpath("//div[contains(text(), 'Телефон')]")
        #TODO

    def extract_info(self):
        table = self.driver.find_elements_by_xpath('//td')
        for i in range(2, len(table), 5):
            name = table[i].text
            number = table[i - 1].text
            condition = table[i - 2].find_elements_by_tag_name('div')[0].get_attribute('title')
            if condition == 'Действующий':
                condition = True
            else:
                condition = False
            address = table[i + 1].text
            scope = table[i + 2].text
            url_for_more_info = table[i].find_elements_by_xpath('.//a')[0].get_attribute('href')
            # TODO: extract info from url
            print()
        return table

    def run(self):
        self.driver.get(self.url)


scraper = Scraper()
scraper.run()
scraper.extract_info()
