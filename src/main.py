import requests
import datetime
import psycopg2
import os
import time
from bs4 import BeautifulSoup
from psycopg2.extras import DictCursor


def exec_query(query_str):
    database_url = os.environ["DATABASE_URL"]
    try:
        with psycopg2.connect(database_url, sslmode='require') as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(query_str)
    except Exception as e:
        print(e.__str__())


def delete_unnecessary_record():
    """
    DBの不要なレコードを削除する。
    """
    dt_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    query_str = f"DELETE FROM weather where target_date < '{str(dt_now)}'"
    exec_query(query_str)


def update_db(output_elem):
    """
    スクレイピングした天気情報をDBに格納する。
    """
    date_str = output_elem["date-str"]
    day_str = output_elem["day-str"]
    weather_str = output_elem["weather-str"]
    high_temp = output_elem["high-temp"]
    low_temp = output_elem["low-temp"]
    rain_chance = output_elem["rain-chance"]
    wind_speed = output_elem["wind-speed"]
    query_str = f"INSERT INTO weather(target_date, day_str, weather_str, high_temp, low_temp, rain_chance, wind_speed) " \
                f"values ('{date_str}', '{day_str}', '{weather_str}', {high_temp}, {low_temp}, {rain_chance}, {wind_speed}) on conflict (target_date)" \
                f"do update set day_str = '{day_str}', weather_str = '{weather_str}', high_temp = {high_temp}, low_temp = {low_temp}, rain_chance = {rain_chance}, wind_speed = {wind_speed};"
    exec_query(query_str)


def fetch_weather_data():
    """
    ディズニーランドの天気情報を取得する。
    """
    # 東京ディズニーランド 10日間天気
    TARGET_URL = "https://tenki.jp/leisure/3/15/80/100001/10days.html"
    res = requests.get(TARGET_URL)
    soup = BeautifulSoup(res.text, 'html.parser')
    forecast_ponst_10days_list = soup.find_all(class_="forecast-point-10days")
    output_dict_list = []
    date_str = ""  # 日付
    day_str = ""  # 曜日
    weather_str = ""  # 天気文字列
    high_temp = -1  # 最高気温
    low_temp = -1  # 最低気温
    rain_chance = -1  # 降水確率
    # 風速については各時間帯の平均をとる
    sum_wind_speed = 0
    count_wind_speed = 0
    mean_wind_speed = -1
    dt_now_jst_aware = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))
    )
    year_str = dt_now_jst_aware.year
    for forecast_ponst_10days in forecast_ponst_10days_list:
        tr_elem_list = forecast_ponst_10days.find_all("tr")
        for i, tr_elem in enumerate(tr_elem_list):
            # 見出し行はスキップ
            if i == 0:
                continue
            if i == len(tr_elem_list) - 1:
                continue
            th_list = tr_elem.find_all("th")
            td_list = tr_elem.find_all("td")
            if len(th_list) != 0:
                if date_str != "" and weather_str != "" and high_temp != -1 and low_temp != -1 and rain_chance != -1:
                    if count_wind_speed != 0:
                        mean_wind_speed = sum_wind_speed / count_wind_speed
                    output_elem = {
                        "date-str": date_str,
                        "day-str": day_str,
                        "weather-str": weather_str,
                        "high-temp": high_temp,
                        "low-temp": low_temp,
                        "rain-chance": rain_chance,
                        "wind-speed": mean_wind_speed
                    }
                    output_dict_list.append(output_elem)
                m_str = th_list[0].get_text().split("月")[0]
                d_str = th_list[0].get_text().split("月")[1].split("日")[0]
                date_str = f"{year_str}-{m_str}-{d_str}"
                day_str = th_list[0].get_text().split("(")[1].strip(")")
                weather_str = th_list[1].get_text()
                high_temp = th_list[2].get_text().split("℃")[0]
                low_temp = th_list[2].get_text().split("℃")[1]
                rain_chance = int(th_list[3].get_text().strip("%"))
            else:
                sum_wind_speed += int(td_list[6].get_text().split("m/s")[0])
                count_wind_speed += 1
    return output_dict_list


def main():
    output_dict_list = fetch_weather_data()
    for output_elem in output_dict_list:
        update_db(output_elem)
        time.sleep(1)
    delete_unnecessary_record()


if __name__ == "__main__":
    main()
