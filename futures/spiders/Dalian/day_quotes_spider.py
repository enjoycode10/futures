#!/usr/bin/env Python3
# -*- coding: utf-8 -*-
# 
# Name   : day_quotes
# Fatures:
# Author : qianyong
# Time   : 2017-06-21 10:14
# Version: V0.0.1
#


"""
Fatures:    大连商品交易所--- 日行情数据
"""
from abc import ABC

from scrapy.spiders import Spider
from scrapy.http import Request, Response, FormRequest
import chardet
import datetime, time, logging
from futures.items.day_quotes import DayQuotesItem

dalian_item = ["豆一", "豆二", "豆粕", "豆油", "棕榈油", "玉米", "玉米淀粉", "鸡蛋", "粳米", "纤维板", "胶合板", "生猪",
               "聚乙烯", "聚氯乙烯", "聚丙烯", "苯乙烯", "焦炭", "焦煤", "铁矿石", "乙二醇", "液化石油气"]


class DayQuotes(Spider, ABC):
    name = 'dalian_day_quotes'

    def start_requests(self):
        url = 'http://www.dce.com.cn/publicweb/quotesdata/dayQuotesCh.html'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/59.0.3071.104 Safari/537.36',
            'Host': 'www.dce.com.cn',
            'Origin': 'http://www.dce.com.cn',
            'Referer': 'http://www.dce.com.cn/publicweb/quotesdata/dayQuotesCh.html'
        }
        the_date_list = self.get_datelist(2393)
        # the_date_list = ['2017-06-17']
        for date_item in the_date_list:
            # date_item = '2017-06-20'
            date_list = date_item.split('-')
            year = date_list[0]
            month = str(int(date_list[1]) - 1)
            day = date_list[2]

            yield FormRequest(url=url,
                              formdata={'day': day, 'dayQuotes.trade_type': '0', 'dayQuotes.variety': 'all',
                                        'month': month, 'year': year}, headers=headers, meta={'data_date': date_item},
                              callback=self.parser)

    def parser(self, response):
        # print(type(response.body))
        # print(response.meta)
        data_date = response.meta.get('data_date', '1971-01-01')
        # encoding = chardet.detect(response.body).get('encoding', 'utf-8')
        # print(encoding)
        # web_text = str(response.body, encoding='utf-8', errors='replace')
        # print(web_text)+
        # print(response.headers)
        data_area_list = response.xpath('//*/div[@class="dataArea"]/*/tr')
        # print(data_area_list.__len__())
        for data_area in data_area_list:
            data = data_area.xpath('td/text()').extract()
            item = [a.strip() for a in data]

            if item:
                if '小计' not in item[0] and '总计' not in item[0]:
                    if item[0] in dalian_item:
                        delivery_month = '20{}-{}-01'.format(item[1][:2], item[1][2:])
                        new_item = [self.format_data(z) for z in item]

                        day_quotes_item = DayQuotesItem()
                        if new_item[0] == '聚乙烯':
                            day_quotes_item['goods_name'] = 'LLDPE'
                        elif new_item[0] == '聚氯乙烯':
                            day_quotes_item['goods_name'] = 'PVC'
                        elif new_item[0] == '聚丙烯':
                            day_quotes_item['goods_name'] = 'PP'
                        else:
                            day_quotes_item['goods_name'] = new_item[0]

                        day_quotes_item['delivery_month'] = delivery_month

                        day_quotes_item['open_price'] = new_item[2]
                        if new_item[2] is None:
                            day_quotes_item['open_price'] = 0
                        day_quotes_item['highest_price'] = new_item[3]
                        if new_item[3] is None:
                            day_quotes_item['highest_price'] = 0
                        day_quotes_item['lowest_price'] = new_item[4]
                        if new_item[4] is None:
                            day_quotes_item['lowest_price'] = 0
                        day_quotes_item['close_price'] = new_item[5]
                        day_quotes_item['pre_settlement_price'] = new_item[6]
                        day_quotes_item['settlement_price'] = new_item[7]
                        day_quotes_item['change_1'] = new_item[8]
                        day_quotes_item['change_2'] = new_item[9]
                        day_quotes_item['deal_volume'] = new_item[10]
                        day_quotes_item['position_volume'] = new_item[11]
                        day_quotes_item['position_volume_change'] = new_item[12]
                        day_quotes_item['deal_amount'] = new_item[13]
                        day_quotes_item['quote_date'] = data_date

                        yield day_quotes_item

                        # logging.info('{}  {}'.format(item.__len__(), item))
                else:
                    logging.info('{} 过滤 小计数据 ：{}'.format(data_date, item))
            else:
                logging.info('清除 空 list')

                # print(response.body)

    def format_data(self, data):
        if data == '-':
            return None
        else:
            return data.replace(',', '')

    def get_datelist(self, day_num):
        """
        获取日期列表
        
        :param day_num: 
        :return: 
        """
        today = datetime.date.today()
        date_list = [(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(day_num)]
        # print(date_list)
        return date_list
