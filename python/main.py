import ujson
import requests
from pyquery import PyQuery as pq
import time
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def naver_weather_crawling(keyword):
    headers = {
        "User-Agent": "PostmanRuntime/7.37.0",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    with requests.Session() as s:
        response = s.get(f'https://search.naver.com/search.naver?query={keyword} 날씨', headers=headers)

        if response.status_code != 200:
            print(f"Failed to get the webpage: {response.status_code}")
            return None

        d = pq(response.content)

        # 날씨 정보 today_weather
        today_weather_list = d('.weather_main .blind').text().split()
        today_weather = today_weather_list[0] if today_weather_list else None

        # 온도 temp
        temp_list = d('.temperature_text strong').text().split()
        temp = temp_list[1].replace("온도", "") if len(temp_list) > 1 else None

        # 어제와 비교 yesterday_summary
        yesterday_summary_list = d('.summary').text().split()
        yesterday_summary = ' '.join(yesterday_summary_list[:3]) if len(yesterday_summary_list) > 2 else None

        summary_list = [item.text() for item in d('.summary_list dd').items()]

        # 체감 temp_feel
        temp_feel = summary_list[0] if summary_list else None
        # 습도 humidity
        humidity = summary_list[1] if summary_list else None

        sub_data = [item.text() for item in d('.today_chart_list .txt').items()]

        # 미세먼지 pm10
        pm10 = sub_data[0] if sub_data else None
        # 자외선 uv
        uv = sub_data[2] if len(sub_data) > 2 else None

        time.sleep(0.1)

        return {
            'today_weather': today_weather,
            'temp': temp,
            'yesterday_summary': yesterday_summary,
            'temp_feel': temp_feel,
            'humidity': humidity,
            'pm10': pm10,
            'uv': uv,
        }


def get_weather_data(request):
    try:
        request_json = request.get_json(silent=True)
        keyword = request_json['keyword']
        weather_data = naver_weather_crawling(keyword)
        time.sleep(0.1)
        return ujson.dumps({
            'resultCode': 200,
            'resultMsg': 'Success',
            'name': keyword,
            'today': weather_data,
        }), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        print(str(e))
        request_json = request.get_json(silent=True)
        keyword = request_json['keyword']
        return ujson.dumps({
            'resultCode': 200,
            'resultMsg': 'False',
            'name': keyword,
            'today': {
                'today_weather': '흐림',
                'temp': '15.3°',
                'yesterday_summary': '어제보다 1.6° 낮아요',
                'temp_feel': '15.3°',
                'humidity': '26%',
                'pm10': '보통',
                'uv': '보통'
            },
        }), 200, {'Content-Type': 'application/json'}
