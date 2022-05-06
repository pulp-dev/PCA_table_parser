import requests
from selenium import webdriver

from lxml.html import fromstring
import xml.etree.ElementTree as ET

import time
from datetime import datetime


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
        self.main_driver = webdriver.Firefox(executable_path=self.driver_path, options=self.options)
        self.secondary_driver = webdriver.Firefox(executable_path=self.driver_path, options=self.options)

        # page
        self.current_page = 1

        # result
        self.data = ET.Element('companies')

    def save(self):
        if self.current_page == 1:
            my_data = ET.tostring(self.data, encoding='unicode', xml_declaration=True)
            new_line = my_data[:-12] + '\n\n' + my_data[-12:]
            with open('results.xml', 'w') as f:
                f.writelines(new_line)
            self.data = ET.Element('companies')
        else:
            my_data = ET.tostring(self.data, encoding='unicode')
            with open('results.xml', 'r') as file:
                lines = file.readlines()

            lines[-2] = my_data[10:-12]
            lines.append(lines[-1])
            lines[-2] = '\n\n'
            self.data = ET.Element('companies')

            with open('results.xml', 'w') as file:
                file.writelines(lines)
        print('data saved')

    def insert_info(self, info):
        company = ET.SubElement(self.data, 'company')
        # id
        company_id = ET.SubElement(company, 'company_id')
        company_id.text = info['id']
        # name
        name = ET.SubElement(company, 'name')
        name.set('lang', "ru")
        name.text = info['name']
        # shortname
        shortname = ET.SubElement(company, 'shortname')
        shortname.set('lang', "ru")
        shortname.text = f'ПТО № {info["id"]}'
        # address
        address = ET.SubElement(company, 'address')
        address.set('lang', "ru")
        address.text = info['address']
        # country
        country = ET.SubElement(company, 'country')
        country.set('lang', "ru")
        country.text = 'Россия'
        # address-add
        el1 = ET.SubElement(company, 'address-add')
        el1.set('lang', "ru")
        # coordinates
        coordinates = ET.SubElement(company, 'coordinates')

        lon = ET.SubElement(coordinates, 'lon')
        lon.text = info['longitude']

        lat = ET.SubElement(coordinates, 'lat')
        lat.text = info['latitude']
        # phone
        phone = ET.SubElement(company, 'phone')

        type_ = ET.SubElement(phone, 'type')
        type_.text = 'phone'

        number = ET.SubElement(phone, 'number')
        number.text = info['phone']

        el2 = ET.SubElement(phone, 'info')
        # email
        email = ET.SubElement(company, 'email')
        email.text = info['email']
        # url
        url1 = ET.SubElement(company, 'url')
        url1.text = info['website']
        url2 = ET.SubElement(company, 'add-url')
        url2.text = info['website']
        url3 = ET.SubElement(company, 'info-page')
        url3.text = info['website']
        # working-time
        el3 = ET.SubElement(company, 'working-time')
        el3.set('lang', "ru")
        # rubric-id
        el4 = ET.SubElement(company, 'rubric-id')
        el4.text = '6615355764'
        # inn, ogrn
        el5 = ET.SubElement(company, 'inn')
        el6 = ET.SubElement(company, 'ogrn')
        # actualization-date
        date = ET.SubElement(company, 'actualization-date')
        date.text = str(datetime.now().date())
        # feature-boolean
        condition = ET.SubElement(company, 'feature-boolean')
        condition.set('name', "pto_stat")
        condition.set('value', f"{info['condition']}")
        # feature-text-single
        scope = ET.SubElement(company, 'feature-text-single')
        scope.set('value', "ts_cats")
        scope.set('name', info['scope'])

    # go for next page
    def next_page(self):
        buttons = self.main_driver.find_elements_by_xpath("//a[@class='ui-commandlink ui-widget']")
        for el in buttons:
            if el.text == str(self.current_page):
                print(f'page: {self.current_page}')
                el.click()
                return
        print()
        raise Exception

    def get_info_from_elements_page(self, elements_url, info):
        self.secondary_driver.get(elements_url)

        time.sleep(0.1)

        wndw = self.secondary_driver.find_elements_by_id('ptoPopup')

        try:
            info['phone'] = wndw[0].find_elements_by_tag_name('p')[-3].text
        except:
            info['phone'] = ''
        try:
            info['email'] = wndw[0].find_elements_by_tag_name('p')[-2].text
        except:
            info['email'] = ''
        try:
            info['website'] = wndw[0].find_elements_by_tag_name('p')[-1].text
        except:
            info['website'] = ''

        try:
            info['latitude'] = \
                wndw[0].find_elements_by_xpath(".//table[@class='table popupTable']")[0].find_elements_by_tag_name('td')[
                    0].text

            info['longitude'] = \
                wndw[0].find_elements_by_xpath(".//table[@class='table popupTable']")[0].find_elements_by_tag_name('td')[
                    1].text
        except Exception as e:
            info['latitude'] = 0
            info['longitude'] = 0
        return info

    def extract_info(self):
        table = self.main_driver.find_elements_by_xpath('//td')
        for i in range(0, len(table), 5):
            try:
                info = {}
                info['name'] = table[i + 2].text
                info['id'] = table[i + 1].text
                condition = table[i].find_elements_by_tag_name('div')[0].get_attribute('title')
                if condition == 'Действующий':
                    info['condition'] = '1'
                else:
                    info['condition'] = '0'
                info['address'] = table[i + 3].text
                info['scope'] = table[i + 4].text
                url_for_more_info = table[i + 2].find_elements_by_xpath('.//a')[0].get_attribute('href')
                info = self.get_info_from_elements_page(url_for_more_info, info)
                self.insert_info(info)
            except IndexError:
                return

    def run(self):
        for i in range(86):
            self.main_driver.get(self.url)
            self.extract_info()
            self.save()
            self.current_page += 1
            try:
                self.next_page()
            except Exception as e:
                print(e)
                print()
                break


scraper = Scraper()
scraper.run()
