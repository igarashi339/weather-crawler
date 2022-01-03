import requests
from bs4 import BeautifulSoup

def main():
    # 東京ディズニーランド 10日間天気
    TARGET_URL = "https://tenki.jp/leisure/3/15/80/100001/10days.html"
    res = requests.get(TARGET_URL)
    soup = BeautifulSoup(res.text, 'html.parser')
    forecast_ponst_10days_list = soup.find_all(class_="forecast-point-10days")
    output_dict_list = []
    date_str = ""  # 日付(曜日)
    weather_str = "" # 天気文字列
    high_temp = -1  # 最高気温
    low_temp = -1   # 最低気温
    rain_chance = -1 # 降水確率
    # 風速については各時間帯の平均をとる
    sum_wind_speed = 0
    count_wind_speed = 0
    mean_wind_speed = -1
    for forecast_ponst_10days in forecast_ponst_10days_list:
        tr_elem_list = forecast_ponst_10days.find_all("tr")
        for i, tr_elem  in enumerate(tr_elem_list):
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
                        "weather-str": weather_str,
                        "high-temp": high_temp,
                        "low-temp": low_temp,
                        "rain-chance": rain_chance,
                        "wind-speed": mean_wind_speed
                    }
                    output_dict_list.append(output_elem)
                date_str = th_list[0].get_text()
                weather_str = th_list[1].get_text()
                high_temp = th_list[2].get_text().split("℃")[0]
                low_temp = th_list[2].get_text().split("℃")[1]
                rain_chance = int(th_list[3].get_text().strip("%"))
            else:
                sum_wind_speed += int(td_list[6].get_text().split("m/s")[0])
                count_wind_speed += 1
    for output_elem in output_dict_list:
        print(output_elem)
                

if __name__ == "__main__":
    main()