from datetime import datetime
from datetime import timedelta
import json
from urllib import parse
from dateutil import rrule
import pandas as pd
import numpy as np


class CharlesSessionParser():
    __filepath = ""
    __uniqid2ptbk_map = {}  # store uniqid=>ptbk map link
    __index_data_list = []

    def __init__(self, filepath) -> None:
        """
        filepath: chlsj文件(json session file)
        """
        self.__filepath = filepath
        pass

    def get_ptbk_by_uniqid(self, uniqid) -> None:
        """
        根据uniqid查询ptbk
        """
        return self.__uniqid2ptbk_map.get(uniqid)

    def load_index_and_ptbk_data(self) -> None:
        """
        从chlsj文件加载指数数据和ptbk（解密使用）
        """
        with open(self.__filepath) as f:
            for session in json.load(f):
                if session['path'] == '/api/SearchApi/index':
                    if session['response']['status'] != 200:
                        continue
                    try:
                        resp = json.loads(session['response']['body']['text'])
                        index_data = {
                            'keyword': resp[
                                'data']['userIndexes'][0]['word'][0]['name'],
                            'content': resp[
                                'data']['userIndexes'][0]['all']['data'],
                            'uniqid': resp['data']['uniqid']
                        }
                        self.__index_data_list.append(index_data)
                    except:
                        pass
                if session['path'] == '/Interface/ptbk':
                    if session['response']['status'] != 200:
                        continue
                    try:
                        params = parse.parse_qs(session['query'])
                        resp = json.loads(session['response']['body']['text'])
                        self.__uniqid2ptbk_map[params['uniqid']
                                               [0]] = resp['data']
                    except:
                        pass

    def decrypt_index_data(self) -> list[dict]:
        """
        完成数据解密
        """
        for index_data in self.__index_data_list:
            try:
                ptbk = self.__uniqid2ptbk_map.get(index_data['uniqid'])
                decrypt_data = decrypt(ptbk, index_data['content'])
                value_list = [int(str)
                              for str in decrypt_data.split(',')]
                index_data['value_num'] = len(value_list)
                index_data['value_list'] = value_list
            except:
                pass
        return self.__index_data_list


def get_week_list_by_date(start_date, end_date) -> list[str]:
    """
    获取指定时间内的所有周列表
    """
    date1 = datetime.strptime(start_date, "%Y-%m-%d")
    date2 = datetime.strptime(end_date, "%Y-%m-%d")
    date_set = set()
    while date1 <= date2:
        year_week = date1.strftime("%Y-%W")
        week = date1.strftime("%W")
        date1 += timedelta(days=1)
        # skip week=0
        if week == '00':
            continue
        date_set.add(year_week)
    date_list = list(date_set)
    date_list.sort()
    return date_list


def decrypt(ptbk, data) -> list[str]:
    """
    基于ptbk解密
    """
    n = len(ptbk)//2
    a = dict(zip(ptbk[:n], ptbk[n:]))
    return "".join([a[s] for s in data])


if __name__ == '__main__':
    output_file = "half_data_result.csv"
    # FIXME: 注意使用网页上实际查出来的起始时间（在图上看第一个点），可能会往前差几天（因为2011-01-01不是所在周的周一）
    start_date = '2010-12-27'
    end_date = '2022-09-22'
    week_list = get_week_list_by_date(start_date, end_date)
    parser = CharlesSessionParser("/Users/xuejian/Downloads/half_data.chlsj")
    parser.load_index_and_ptbk_data()
    index_data_list = parser.decrypt_index_data()
    all_result = pd.DataFrame()
    for index_data in index_data_list:
        result = pd.DataFrame()
        try:
            result['value'] = index_data['value_list']
            result['keyword'] = index_data['keyword']
            result['week'] = week_list
            all_result = pd.concat([all_result, result])
        except:
            pass
    print(all_result)
    all_result.to_csv(output_file)
