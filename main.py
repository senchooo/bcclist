import glob
import json
import time
import geocoder
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd


s = Service(r'D:\download\chromedriver')
driver = webdriver.Chrome(service=s)


def login(user, passw):
    driver.get('https://www.bccondosandhomes.com/login?')
    while True:
        try:
            log = WebDriverWait(driver, 90).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="firebaseui-auth-container"]/div/div[1]/form/ul/li[2]/button')))
            log.click()
            time.sleep(3)
            break
        except Exception:
            driver.refresh()
            print('waiting for login')
    username = driver.find_element(By.XPATH, '//*[@id="firebaseui-auth-container"]/div/form/div[2]/div/div[1]/input')
    username.send_keys(user)
    time.sleep(3)
    driver.find_element(By.XPATH, '//*[@id="firebaseui-auth-container"]/div/form/div[3]/div/button[2]').click()
    time.sleep(3)

    password = driver.find_element(By.XPATH, '//*[@id="firebaseui-auth-container"]/div/form/div[2]/div[3]/input')
    password.send_keys(passw)
    time.sleep(3)
    driver.find_element(By.XPATH, '//*[@id="firebaseui-auth-container"]/div/form/div[3]/div[2]/button').click()
    time.sleep(5)

    try:
        driver.find_element(By.XPATH, '//*[@id="complete-profile"]/div[7]/button').click()
    except Exception:
        pass
    print('login complete')
    time.sleep(10)


def scrap(page, key, urll):
    driver.get(urll)
    data = []
    # for iteration
    plus = 1
    err = 0

    # for next page
    for a in range(0, page):
        # handling error for visibility mainpage
        while True:
            try:
                mainpage = WebDriverWait(driver, 90).until(EC.visibility_of_all_elements_located((By.XPATH, '//div[@class="listing__content"]')))
                time.sleep(5)
                break
            except Exception:
                driver.refresh()

        for i in mainpage:
            # get href & open in new tab
            href = i.find_elements(By.TAG_NAME, 'a')[0].get_attribute('href')
            driver.execute_script(f'window.open("{href}")')
            driver.switch_to.window(driver.window_handles[1])

            # scrap link, title, status, description
            time.sleep(10)
            link = driver.current_url
            source = driver.page_source
            soup = BeautifulSoup(source, 'html.parser')

            # for skip if link is server error
            try:
                title = soup.find('div', 'listing-detail__address listing-detail-page__address').get_text().strip().split(',')[0]
            except Exception:
                err += 1
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue

            status = soup.find('div', {'class': 'listing-detail-status'}).find('span').get_text().replace(' ', '')

            # get price info from main if url == active listing
            if urll == 'https://www.bccondosandhomes.com/search-listings/':
                price = soup.find('div', {'class': 'listing-detail__price listing-detail__price--mortgage'}).get_text().strip()
                pricedate = '-'
                sold = 'not sold'
                solddate = 'not sold'
            else:
                history = soup.find('div', {'class': 'listing-detail__history-table table-responsive'})
                sold = history.find('td', string='Sold').parent.findAll('td')[3].get_text().strip()
                solddate = history.find('td', string='Sold').parent.findAll('td')[0].get_text()
                price = history.find('td', string='Active').parent.findAll('td')[3].get_text().strip()
                pricedate = history.find('td', string='Active').parent.findAll('td')[0].get_text()

            # scrap in main description
            finddet = soup.find('div', {'class': 'listing-detail__details-items row clearfix'})
            try:
                beds = finddet.find('div', string='Beds').parent.findAll('div')[1].get_text()
            except Exception:
                beds = ''

            try:
                bath = finddet.find('div', string='Bath').parent.findAll('div')[1].get_text()
            except Exception:
                bath = ''

            try:
                lot = finddet.find('div', string='Lot Size').parent.findAll('div')[1].get_text()
            except Exception:
                lot = ''

            # scrap in description table
            findtabel = soup.find('div', {'class': 'listing-detail__technical listing-detail--border'}).find('table', {'class': 'table table-striped'})
            mls = findtabel.find('td', string='MLS® #').parent.findAll('td')[1].get_text()
            typehouse = findtabel.find('td', string='Property Type').parent.findAll('td')[1].get_text()
            city = findtabel.find('td', string='City').parent.findAll('td')[1].get_text()
            listed = findtabel.find('td', string='Listed By').parent.findAll('td')[1].get_text()
            year = findtabel.find('td', string='Year Built').parent.findAll('td')[1].get_text()
            try:
                kitchen = findtabel.find('td', string='Kitchens').parent.findAll('td')[1].get_text()
            except Exception:
                kitchen = '-'
            try:
                tax = findtabel.find('td', string='Tax').parent.findAll('td')[1].get_text()
            except Exception:
                tax = ''
            try:
                parking = findtabel.find('td', string='Parking').parent.findAll('td')[1].get_text()
            except Exception:
                parking = ''

            try:
                desc = soup.find('div', {'class': 'listing-detail__description listing-detail--border'}).find('p').get_text()
            except Exception:
                desc = '-'

            try:
                floorr = soup.find('div', {'class': 'listing-detail__floor--area listing-detail--border'}).find('table', {'class': 'table table-striped'})
                floor = floorr.find('td', string='Total').parent.findAll('td')[1].get_text()
            except Exception:
                floor = '-'

            try:
                feature = soup.find('div', {'class': 'listing-detail__features listing-detail--border'}).get_text().strip().replace('Features\n', '').replace('\n', ' ')
            except Exception:
                feature = '-'

            try:
                influence = soup.find('div', {'class': 'listing-detail__site listing-detail--border'}).get_text().strip().replace('Site Influences\n', '').replace('\n', ' ')
            except Exception:
                influence = '-'

            try:
                amenities = soup.find('div', {'class': 'listing-detail__amenities listing-detail--border'}).get_text().strip().replace('Amenities', '').replace('\n', ' ')
            except Exception:
                amenities = '-'

            try:
                leveling = soup.find('div', {'class': 'listing-detail__technical listing-detail--border'}).find('table', {'class': 'table table-striped'})
                level = leveling.find('td', string='Levels:').parent.findAll('td')[1].get_text()
            except Exception:
                level = '-'

            # scrap len image
            imgg = soup.find('div', {'id': 'listing-detail__images'}).findAll('a')
            img = len(imgg)

            # scrap address & gps
            try:
                lab = driver.find_element(By.XPATH, '//div[@class="listing-detail__map"]')
                driver.execute_script('arguments[0].scrollIntoView(true)', lab)
                time.sleep(10)
                driver.switch_to.frame(driver.find_element(By.TAG_NAME, 'iframe'))

                a = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="mapDiv"]/div/div/div[4]/div/div/div/div/div[1]/div[2]')))
                address = a.text
                loc = address.replace('#', '').replace('#', '')
                g = geocoder.tomtom(loc, key=key)
                gps = g.latlng
                if gps is None:
                    gps = ''

                driver.switch_to.frame(0)

            except Exception:
                address = findtabel.find('td', string='Address').parent.findAll('td')[1].get_text()
                gps = ''

            # data
            datt = {
                'MLS': mls,
                'Property': title,
                'Status': status,
                'Type': typehouse,
                'City': city,
                'Sold Price': sold,
                'Sold Date': solddate,
                'List Price': price,
                'List Date': pricedate,
                'Bed': beds,
                'Bath': bath,
                'Kitchen': kitchen,
                'Tax': tax,
                'year': year,
                'Floor': floor,
                'Lot': lot,
                'Levels': level,
                'Parking': parking,
                'Photos': img,
                'Address': address,
                'GPS': ', '.join(map(str, gps)),
                'URL': link,
                'Agency': listed,
                'Description': desc,
                'Feature': feature,
                'Influence': influence,
                'Amenities': amenities
            }
            data.append(datt)
            print(f'{plus}. {datt}')

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            plus += 1

        # click next page
        driver.find_element(By.XPATH, '//a[@class="page-link false"]').click()

    # create csv & json data
    df = pd.DataFrame(data)
    if urll == 'https://www.bccondosandhomes.com/search-listings/':
        df.to_csv(f'result {page} page from active listing.csv', index=False)
        with open(f'result {page} page from active listing.json', 'w+') as jsonfile:
            json.dump(data, jsonfile)
    else:
        df.to_csv(f'result {page} page from sold listing.csv', index=False)
        with open(f'result {page} page from sold listing.json', 'w+') as jsonfile:
            json.dump(data, jsonfile)

    print('all page has scraped')
    print(f'data not available: {err}')


def run():
    change = int(input('1. scrap active listing\n2. scrap sold listing\n3. scrap all listing\ninput here: '))
    if change == 1:
        a = int(input('How Many Pages (1 page = 200 data): '))
        b = input('Input Your TomTom API Keys: ')
        c = 'https://www.bccondosandhomes.com/search-listings/'
        scrap(a, b, c)

    if change == 2:
        uss = input('Type Your Email: ')
        pww = input('Type Your Password: ')
        a = int(input('How Many Pages (1 page = 200 data): '))
        b = input('Input Your TomTom API Keys: ')
        c = 'https://www.bccondosandhomes.com/search-listings/?listing_status=sold'
        login(uss, pww)
        scrap(a, b, c)

    if change == 3:
        uss = input('Type Your Email: ')
        pww = input('Type Your Password: ')
        a = int(input('How Many Active & Sold Listing Pages (1 page = 200 data): '))
        b = input('Input Your TomTom API Keys: ')
        c = ['https://www.bccondosandhomes.com/search-listings/', 'https://www.bccondosandhomes.com/search-listings/?listing_status=sold']

        login(uss, pww)
        for i in c:
            scrap(a, b, i)

        # read & create merge file
        filejson = sorted(glob.glob('*.json'))
        datas = []
        for j in filejson:
            with open(j) as jsonfile:
                data = json.load(jsonfile)
                datas.extend(data)
        df = pd.DataFrame(datas)
        df.to_csv('all data from active & sold listing.csv', index=False)
        with open('all data from active & sold listing.json', 'w+') as outfile:
            json.dump(datas, outfile)


run()



