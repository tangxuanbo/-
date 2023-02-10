import time
import requests as rq
from bs4 import BeautifulSoup as bs
import csv
import re

debug = False
csv_menu = []                   # 请求头信息 : UA:身份认证  Cookie:Cookie有过期时间,过期之后就无法获取数据了,需要更换Cookie
sleep_time = 3                  # chrome浏览器 # edge浏览器
headers1 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
    'Cookie': 'antipas=42753262W9207405H3363169981'
}
headers2 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66',
    'Cookie': 'antipas=2N7593105499097086O91792XO'
}
headers = [headers1, headers2]
# 请求城市页面获取车辆url
def getCarUrl(city_url, car_brif):
    count = 0
    count_all = 0
    base_url = 'https://www.guazi.com'
    for city in city_url:
        try:
            myheaders = headers[count_all % len(headers)]
            print('正在获取：' + city)
            pages = 51
            if debug:
                pages = 2
            for index in range(1, pages):
                try:
                    print('正在获取' + city + '：第' + str(index) + ' 页')
                    # 1.url
                    url = 'https://www.guazi.com/' + city + '/buy/o' + str(index) + '/#bread'
                    # 2.模拟浏览器发送请求,接受响应
                    respones = rq.get(url=url, headers=myheaders, timeout=3)
                    # 3.网页解析
                    if respones.status_code == 200:
                        text = respones.content.decode('utf-8')
                        raw_html = bs(text, 'lxml')  # 返回网页
                        car_ul = raw_html.select_one('.carlist')  # <ul class="carlist clearfix js-top"># ul
                        # 获取car_ul中的a标签
                        car = car_ul.select('a')
                        for c in car:
                            # 原价
                            try:
                                original_price = c.select('.line-through')[0].get_text()
                                car_brif[base_url + c.get('href')] = original_price
                                # 每个城市获取条目计数
                                count += 1
                            except:
                                continue
                    else:
                        print('respones.status_code' + str(respones.status_code))
                except:
                    continue
            count_all += count
            print(city + '共获取：' + str(count) + '条')
            count = 0
        except:
            continue
    print('\n所有城市共获取：' + str(count_all) + '条')
# 请求车辆页面获取数据
def getCarDetail(car_brif):
    count = 0
    count10 = 0
    car_info_list = []
    print('\n获取信息ing...')
    for url in car_brif:
        # 防止网站反爬拒绝访问导致整个程序崩溃
        try:
            myheaders = headers[count % len(headers)]
            respones = rq.get(url=url, headers=myheaders, timeout=5)
            if respones.status_code == 200:
                text = respones.content.decode('utf-8')
                raw_html = bs(text, 'lxml')  # 返回car页面
                city = raw_html.select_one('title').text[0:2].strip()# 城市
                title = raw_html.select_one('.titlebox').text.strip()# 名称
                searchObj1 = re.search(r'([\u4e00-\u9fa5]+.).+', title, re.I)
                if searchObj1:
                    real_title = searchObj1.group().replace('\r', '')
                else:
                    real_title = 'null'

                brand = real_title.split(' ', 1)[0].strip()# 品牌
                searchObj2 = re.search(r'\d\d\d\d', real_title, re.I)
                if searchObj2:
                    year = searchObj2.group()
                else:
                    year = 'None'# 上牌时间
                info = raw_html.select('ul.assort span')# 车辆信息
                length = info[1].text.strip()# 表显里程
                power = info[2].text.strip()# 排量
                gearbox = info[3].text.strip()# 变速箱
                original_price = car_brif[url];# 原价
                price = raw_html.select('div.price-main span')[0].get_text().strip()# 售价
                basic_eleven_info = raw_html.select_one('.basic-eleven')
                emission_standard = basic_eleven_info.select_one('.four').get_text().split("\n")[1].strip()# 排放标准
                transfer_times = basic_eleven_info.select_one('.seven').get_text().split("\n")[1].strip()# 过户次数
                use_type = basic_eleven_info.select_one('.nine').get_text().strip()# 使用性质
                right_type = basic_eleven_info.select_one('.ten').get_text().strip()# 产权性质
                watching_mode = basic_eleven_info.select_one('.eight').get_text().strip()# 看车方式
                abnormal = raw_html.select('.fc-org-text')
                abnormal_num = 0
                for i in range(1, len(abnormal)):
                    abnormal_num += int(raw_html.select('.fc-org-text')[i].text[0:-3])# 异常点
                # 详细配置
                detail_content = raw_html.select_one('.detailcontent').select('table')
                carlwh = detail_content[0].select('td')[11].text.strip()# 车长/宽/高
                wheelbase = detail_content[0].select('td')[13].text.strip()# 轴距
                cargo_volume = detail_content[0].select('td')[15].text.strip()# 行李箱容积
                curb_weight = detail_content[0].select('td')[17].text.strip()# 整备质量
                air_form = detail_content[1].select('td')[3].text.strip()# 进气形式
                cylinder = detail_content[1].select('td')[5].text.strip()# 气缸数
                max_horsepower = detail_content[1].select('td')[7].text.strip()# 最大马力
                max_torque = detail_content[1].select('td')[9].text.strip()# 最大扭矩
                fuel_type = detail_content[1].select('td')[11].text.strip()# 燃料类型
                oil_type = detail_content[1].select('td')[13].text.strip()# 燃油标号
                oil_supply_form = detail_content[1].select('td')[15].text.strip()# 供油方式
                car = {
                    '城市':
                        city,
                    '名称':
                        real_title,
                    '上牌时间':
                        year,
                    '品牌':
                        brand,
                    '表显里程':
                        length,
                    '排量':
                        power,
                    '变速箱':
                        gearbox,
                    '原价':
                        original_price,
                    '售价':
                        price,
                    '排放标准':
                        emission_standard,
                    '过户次数':
                        transfer_times,
                    '使用性质':
                        use_type,
                    '产权性质':
                        right_type,
                    '看车方式':
                        watching_mode,
                    '异常点':
                        abnormal_num,
                    '车长/宽/高':
                        carlwh,
                    '轴距':
                        wheelbase,
                    '行李箱容积':
                        cargo_volume,
                    '整备质量':
                        curb_weight,
                    '进气形式':
                        air_form,
                    '气缸数':
                        cylinder,
                    '最大马力':
                        max_horsepower,
                    '最大扭矩':
                        max_torque,
                    '燃料类型':
                        fuel_type,
                    '燃油标号':
                        oil_type,
                    '供油方式':
                        oil_supply_form
                }
            else:
                print('respones.status_code' + str(respones.status_code))
        except:
            continue
        # 将字典加入汽车信息(car_info_list)列表
        car_info_list.append(car)
        # 计数+1
        count += 1;
        # 只写一条数据测试
        if debug:
            break;
        # 整10输出，并清零计数，并休眠两秒（防反爬）
        if (count % 10) == 0:
            count10 += count
            print('正在提取数据，已获取：' + str(count10) + '条')
            time.sleep(0.2)
            count = 0
    print('\n正在提取数据，已获取：' + str(len(car_info_list)) + ' 条')
    for key in car.keys():
        csv_menu.append(key)
    return car_info_list
# 储存数据
def save_csv(car_info_list):
    print('\n正在将数据插入表格...')
    file = open('瓜子二手车.csv', 'w', newline='', encoding='utf-8')
    csvWriter = csv.writer(file)
    csvWriter.writerow(csv_menu)
    for item in car_info_list:
        # 按行写入
        csv_dat = []
        for i in range(0, len(csv_menu)):
            csv_dat.append(item.get(csv_menu[i]))
        csvWriter.writerow(csv_dat)
    file.close()
if __name__ == '__main__':
    city_url = ['hz']# (每个城市的url)杭州 北京 上海 成都 重庆,'yc','qf'
    # 车辆页面的url与车的原价
    car_brif = {}
    car_brif = {}
    getCarUrl(city_url, car_brif)# 使用字典可以做到自动去重
    car_info_list = getCarDetail(car_brif)# 获取到的车辆信息
    save_csv(car_info_list)# 储存