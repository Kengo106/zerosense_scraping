from time import sleep
from itertools import islice
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from django.db import transaction
from .models import Race, Horse, HorsePlace, Odds
import os
import time
import re
from datetime import datetime
import traceback
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import pytz
# scraping.pyのディレクトリを取得


def initialize_browser():
    # Chrome WebDriverのパスを指定
    # script_dir = os.path.dirname(os.path.abspath(__file__))

    # WebDriverのパスを指定
    webdriver_path = os.path.join("/opt/chrome/chromedriver-linux64", "chromedriver")

    # Chromeの実行可能ファイルのパスを指定
    # chrome_options = Options()
    # chrome_options.binary_location = r'C:\Users\81806\Desktop\python\JRA\zerosence\app1\chrome\win64-114.0.5735.133\chrome-win64\chrome.exe'

    # Chromeのヘッドレスオプションを設定する(GUIなし)
    chrome_options = Options()
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--no-sandbox")  # サンドボックス無効化
    chrome_options.add_argument("--disable-dev-shm-usage")  # /dev/shmパーティションの使用を制限


    # Serviceオブジェクトを作成
    service = Service(webdriver_path)

    # Chromeを起動
    browser = webdriver.Chrome(service=service, options=chrome_options)

    return browser


def scrape_grade_race(browser):

    # 起動したWebDriverにJRAのURLを入力
    url = "https://www.jra.go.jp/"
    browser.get(url)

    elem_quick_menu = browser.find_element(
        By.ID, "quick_menu")  # 上のクイックメニューを選択
    elem_quick_menu_list = elem_quick_menu.find_elements(
        By.TAG_NAME, "li")  # クイックメニューから出馬表を指定するためにliタグを指定
    elem_race = elem_quick_menu_list[1]  # 左から2項目の出馬表を選択

    elem_race.click()
    time.sleep(1)  # プログラムを一時停止

    grade_races = []

    grade_race = browser.find_element(By.ID, "grade_race")  # 重賞表示個所に移動
    race_grade_imgs = grade_race.find_elements(
        By.TAG_NAME, "img")  # グレートを表す画像を取得
    grade_num = len(race_grade_imgs)
    for i in range(grade_num):
        grade_race = browser.find_element(By.ID, "grade_race")  # 重賞表示個所に移動
        race_grade_imgs = grade_race.find_elements(
            By.TAG_NAME, "img")  # グレートを表す画像を取得
        race_grade = race_grade_imgs[i].get_attribute('alt')  # グレートを取得
        race_grade_imgs[i].click()  # レース出走馬画面に移動
        sleep(1)
        race_name = browser.find_element(By.CLASS_NAME, "race_name")  # レース名を取得
        race_time = browser.find_element(By.CLASS_NAME, "date_line").find_element(
            By.CSS_SELECTOR, ".cell.time").find_element(By.TAG_NAME, "strong")

        dt = datetime.strptime(race_time.text, "%H時%M分")
        race_time_replace = dt.time()
        race_date = browser.find_element(
            By.CSS_SELECTOR, ".cell.date")  # レース日を取得
        # .date()は年月日だけのオブジェクトをかえす
        race_date_object = datetime.strptime(re.search(
            r"(\d{4}年\d{1,2}月\d{1,2}日)", race_date.text).group(0), '%Y年%m月%d日').date()
        horse_table = browser.find_element(By.ID, "syutsuba")  # 出馬表に移動
        horse_infos = horse_table.find_elements(
            By.CLASS_NAME, "horse")  # 表内の出走馬が表示される列を取得

        for horse_info in horse_infos[1:]:  # 馬情報が載っている列を一行づつ取得(ヘッダーを省く)
            grade_race_datum = {}
            horse_name = horse_info.find_element(
                By.CLASS_NAME, "name")  # 馬名を取得
            grade_race_datum["grade"] = race_grade
            grade_race_datum["race_name"] = race_name.text
            grade_race_datum["horse_name"] = horse_name.text
            grade_race_datum["start_time"] = race_time_replace
            grade_race_datum["race_date"] = race_date_object
            grade_races.append(grade_race_datum)

        browser.back()

    with transaction.atomic():
        for grade_race in grade_races:
            game_race, _ = Race.objects.update_or_create(
                race_name=grade_race["race_name"],
                defaults={
                    'rank': grade_race["grade"],
                    'race_date': grade_race["race_date"],
                    'start_time': grade_race["start_time"],
                    'is_votable': 1
                }
            )
            try:

                Horse.objects.update_or_create(
                    race=game_race,
                    horse_name=grade_race["horse_name"],
                )

            except:
                print(grade_race["horse_name"])

    return browser.quit()  # ブラウザを閉じる


def get_data(soup, race_name, grade_races_odds, grade_races):
    tbody = soup.find('tbody')
    places = tbody.find_all('td', class_='place')
    horses = tbody.find_all('td', class_='horse')

    refunds = soup.find('div', class_='refund_unit mt15')
    tan = refunds.find("li", class_="win").find(
        'div', class_="yen").text.replace("円", "").replace(",", "")
    if len([yen.find('div', class_="yen").text.replace(
            "円", "").replace(",", "") for yen in refunds.find("li", class_="place").find_all("div", "line")]) != 3:
        print('error')
        print(race_name)
        print([yen.find('div', class_="yen").text.replace("円", "").replace(",", "")
               for yen in refunds.find("li", class_="place").find_all("div", "line")])
    fuku_1, fuku_2, fuku_3 = [yen.find('div', class_="yen").text.replace(
        "円", "").replace(",", "") for yen in refunds.find("li", class_="place").find_all("div", "line")][:3]
    umaren = refunds.find("li", class_="umaren").find(
        'div', class_="yen").text.replace("円", "").replace(",", "")
    umatan = refunds.find("li", class_="umatan").find(
        'div', class_="yen").text.replace("円", "").replace(",", "")
    wide_12, wide_13, wide_23 = [yen.find('div', class_="yen").text.replace(
        "円", "").replace(",", "") for yen in refunds.find("li", class_="wide").find_all("div", "line")][:3]

    trio = refunds.find("li", class_="trio").find(
        'div', class_="yen").text.replace("円", "").replace(",", "")
    tierce = refunds.find("li", class_="tierce").find(
        'div', class_="yen").text.replace("円", "").replace(",", "")
    odds_datamu = {}
    odds_datamu["race_name"] = race_name
    odds_datamu['tan'] = tan
    odds_datamu['fuku_1'] = fuku_1
    odds_datamu['fuku_2'] = fuku_2
    odds_datamu['fuku_3'] = fuku_3
    odds_datamu['umaren'] = umaren
    odds_datamu['umatan'] = umatan
    odds_datamu['wide_12'] = wide_12
    odds_datamu['wide_13'] = wide_13
    odds_datamu['wide_23'] = wide_23
    odds_datamu['trio'] = trio
    odds_datamu['tierce'] = tierce

    grade_races_odds.append(odds_datamu)

    for place, horse in zip(places, horses):
        race_datamu = {}
        race_datamu['race_name'] = race_name
        race_datamu["place"] = place.text.strip()
        race_datamu["horse_name"] = horse.text.strip()
        grade_races.append(race_datamu)
    sleep(1)


def scrape_grade_race_result(browser):

    # 起動したWebDriverにJRAのURLを入力
    url = "https://www.jra.go.jp/"
    browser.get(url)

    elem_quick_menu = browser.find_element(
        By.ID, "quick_menu")  # 上のクイックメニューを選択
    elem_quick_menu_list = elem_quick_menu.find_elements(
        By.TAG_NAME, "li")  # クイックメニューから出馬表を指定するためにliタグを指定
    elem_race = elem_quick_menu_list[3]  # 左から4項目のレース結果を選択

    elem_race.click()
    time.sleep(1)  # プログラムを一時停止

    grade_races = []
    grade_races_odds = []

    latest_grade_race_num = len(browser.find_element(
        By.ID, "grade_race").find_elements(By.CLASS_NAME, 'race_num'))
    for i in range(min(latest_grade_race_num, 10)):  # 先週の重賞結果を取得
        grade_races_elements = browser.find_element(
            By.ID, "grade_race").find_elements(By.CLASS_NAME, 'race_num')

        grade_races_elements[i].click()  # 順番にレースページへ

        soup = BeautifulSoup(browser.page_source,
                             "html.parser")  # seleniumからbsへ変換

        race_name = soup.find('div', id='race_result').find(
            'span', class_="race_name").text  # ここでレース名を取得しないと短縮形になる

        tbody = soup.find('tbody')
        places = tbody.find_all('td', class_='place')
        horses = tbody.find_all('td', class_='horse')

        refunds = soup.find('div', class_='refund_unit mt15')
        tan = refunds.find("li", class_="win").find(
            'div', class_="yen").text.replace("円", "").replace(",", "")
        fuku_1, fuku_2, fuku_3 = [yen.find('div', class_="yen").text.replace(
            "円", "").replace(",", "") for yen in refunds.find("li", class_="place").find_all("div", "line")]
        umaren = refunds.find("li", class_="umaren").find(
            'div', class_="yen").text.replace("円", "").replace(",", "")
        umatan = refunds.find("li", class_="umatan").find(
            'div', class_="yen").text.replace("円", "").replace(",", "")
        wide_12, wide_13, wide_23 = [yen.find('div', class_="yen").text.replace(
            "円", "").replace(",", "") for yen in refunds.find("li", class_="wide").find_all("div", "line")]

        trio = refunds.find("li", class_="trio").find(
            'div', class_="yen").text.replace("円", "").replace(",", "")
        tierce = refunds.find("li", class_="tierce").find(
            'div', class_="yen").text.replace("円", "").replace(",", "")
        odds_datamu = {}
        odds_datamu["race_name"] = race_name
        odds_datamu['tan'] = tan
        odds_datamu['fuku_1'] = fuku_1
        odds_datamu['fuku_2'] = fuku_2
        odds_datamu['fuku_3'] = fuku_3
        odds_datamu['umaren'] = umaren
        odds_datamu['umatan'] = umatan
        odds_datamu['wide_12'] = wide_12
        odds_datamu['wide_13'] = wide_13
        odds_datamu['wide_23'] = wide_23
        odds_datamu['trio'] = trio
        odds_datamu['tierce'] = tierce

        grade_races_odds.append(odds_datamu)

        for place, horse in zip(places, horses):
            race_datamu = {}
            race_datamu['race_name'] = race_name
            race_datamu["place"] = place.text.strip()
            race_datamu["horse_name"] = horse.text.strip()
            grade_races.append(race_datamu)

        sleep(1)
        browser.back()

    grade_races_elements_num = len(browser.find_elements(
        By.CLASS_NAME, "race"))  # 取得対象のレース数を取得

    for i in range(min(grade_races_elements_num, 10)):  # 過去10レース分を取得
        list_grade_races_elements = browser.find_elements(
            By.CLASS_NAME, "race")

        list_one_place_races = list_grade_races_elements[i].find_elements(
            By.TAG_NAME, 'a')
        print([a.text for a in list_one_place_races])

        if len(list_one_place_races)-1:
            for num in range(len(list_one_place_races)):
                print(num)
                # 順番にレースページへ
                list_grade_races_elements = browser.find_elements(
                    By.CLASS_NAME, "race")

                list_one_place_races = list_grade_races_elements[i].find_elements(
                    By.TAG_NAME, 'a')
                # print([a.text for a in list_one_place_races])
                # print(len(list_one_place_races), 'です')
                # sleep(5)

                list_one_place_races[num].click()
                soup = BeautifulSoup(browser.page_source,
                                     "html.parser")
                race_name = soup.find('div', id='race_result').find(
                    'span', class_="race_name").text
                # sleep(5)
                print(race_name)
                get_data(soup, race_name, grade_races_odds, grade_races)
                browser.back()

        else:
            list_one_place_races[0].click()

            soup = BeautifulSoup(browser.page_source,
                                 "html.parser")  # seleniumからbsへ変換

            race_name = soup.find('div', id='race_result').find(
                'span', class_="race_name").text  # ここでレース名を取得しないと短縮形になる
            print(race_name)
            get_data(soup, race_name, grade_races_odds, grade_races)
            browser.back()

    with transaction.atomic():
        for grade_race_odds in grade_races_odds:
            try:
                utc_now = timezone.now()
                jst = pytz.timezone('Asia/Tokyo')
                jst_now = utc_now.astimezone(jst)
                now_date = jst_now.date()
                update_count = Race.objects.filter(
                    race_name=grade_race_odds["race_name"], race_date__lte=now_date - timedelta(day=4)).update(is_votable=0)
                print(update_count)
                race = Race.objects.get(race_name=grade_race_odds["race_name"])
                Odds.objects.update_or_create(
                    race=race,
                    defaults={
                        'tan': int(grade_race_odds["tan"]),
                        'fuku_1': int(grade_race_odds["fuku_1"]),
                        'fuku_2': int(grade_race_odds["fuku_2"]),
                        'fuku_3': int(grade_race_odds["fuku_3"]),
                        'umaren': int(grade_race_odds["umaren"]),
                        'umatan': int(grade_race_odds["umatan"]),
                        'wide_12': int(grade_race_odds["wide_12"]),
                        'wide_13': int(grade_race_odds["wide_13"]),
                        'wide_23': int(grade_race_odds["wide_23"]),
                        'trio': int(grade_race_odds["trio"]),
                        'tierce': int(grade_race_odds["tierce"]),
                    }
                )
            except Race.DoesNotExist:
                print(
                    f"Race with name {grade_race_odds['race_name']} does not exist.")
            except Exception as e:
                print("ERROR! odds")
                print(str(e))
                traceback.print_exc()
        for grade_race in grade_races:
            try:
                race = Race.objects.get(race_name=grade_race["race_name"])
                horse, _ = Horse.objects.get_or_create(
                    race=race, horse_name=grade_race["horse_name"])
                if grade_race["place"].isdigit():
                    place = int(grade_race["place"])
                    HorsePlace.objects.update_or_create(
                        horse=horse,  # フィルタリングキーの指定　ない場合はHorse=horseでcreateされる
                        defaults={
                            "place": place
                        }
                    )
                else:
                    place = 999
                    HorsePlace.objects.update_or_create(
                        horse=horse,
                        defaults={
                            "place": place
                        }
                    )
                    print(grade_race["horse_name"], grade_race["place"])
            except Race.DoesNotExist:
                print(
                    f"Race with name {grade_race_odds['race_name']} does not exist.")
            except Exception as e:
                print("ERROR! result")
                print(str(e))
                traceback.print_exc()

    return browser.quit()  # ブラウザを閉じる

