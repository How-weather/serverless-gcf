import requests
import ujson

from bs4 import BeautifulSoup
from pprint import pprint

def naver_weather_crawling(keyword):
    html = requests.get(f'https://search.naver.com/search.naver?query={keyword} 날씨')
    soup = BeautifulSoup(html.text, 'html.parser')

    body = soup.find('div', {'class': 'content_wrap'})

    with open('./mock.json') as f:
        time_data = ujson.load(f)

    # 날씨 정보 today_weather
    today_weather = body.find('div', {'class': 'weather_main'}).find('span', {'class': 'blind'}).text

    # 온도 temp
    temp = body.find('div', {'class': 'temperature_text'}).find('strong')
    blind_span = temp.find('span', {'class': 'blind'})
    if blind_span:
        blind_span.extract()

    # 어제와 비교 yesterday_summary
    yesterday_summary = body.find('p', {'class': 'summary'})
    p_slash = yesterday_summary.find('span', {'class': 'weather before_slash'})
    if p_slash:
        p_slash.extract()

    summary_list = body.find('dl', {'class': 'summary_list'})

    # 체감 temp_feel
    temp_feel = summary_list.findAll('dd')[0].text
    # 습도 humidity
    humidity = summary_list.findAll('dd')[1].text

    sub_data = body.find('ul', {'class': 'today_chart_list'}).findAll('span', {'class': 'txt'})
    # 미세먼지 pm10
    pm10 = sub_data[0].text
    # 자외선 uv
    uv = sub_data[2].text

    # li_items = body.find('div', {'class': 'graph_inner _hourly_weather'}).find('ul').find_all('li')
    # time_data = []
    # for item in li_items:
    #     # 시간, 날씨 상태, 온도 추출
    #     time = item.find('dt', class_='time').text.strip()
    #     weather = item.find('span', class_='blind').text.strip()
    #     degree = item.find('span', class_='num').text.strip()
    #
    #     # 추출한 데이터를 딕셔너리로 구성
    #     weather_dict = {
    #         'time': time,
    #         'weather': weather,
    #         'degree': degree
    #     }
    #
    #     time_data.append(weather_dict)

    return {
        'today': {
            'today_weather': today_weather,
            'temp': temp.text,
            'yesterday_summary': yesterday_summary.text.strip(),
            'temp_feel': temp_feel,
            'humidity': humidity,
            'pm10': pm10,
            'uv': uv,
        },
        'time': time_data
    }

def get_weather_data(request):
    try:
        request_json = request.get_json(silent=True)
        locate = request_json['locate']
        if isinstance(locate, str):
            locate = ujson.loads(locate)
        weather_data = naver_weather_crawling(locate['name'])
        # pprint(weather_data)
        return ujson.dumps({
            'resultCode': '200',
            'resultMsg': 'Success',
            'name': locate['name'],
            'today': weather_data['today'],
            'time': weather_data['time'],
        }), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return ujson.dumps({
            'resultCode': '400',
            'resultMsg': str(e),
            'name': None,
            'now': None,
        }), 200, {'Content-Type': 'application/json'}
