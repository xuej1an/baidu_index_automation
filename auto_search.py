from datetime import *
from multiprocessing.connection import wait
from dateutil import rrule
import json
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def read_keywords_by_dta(filepath):
    """
    从dta文件读取关键字

    input: dta file (columns: stkcd,name_simple,name)
    output:
    - code_list_result: string[] 股票代码列表
    - name_list_result: string[] 股票名称列表
    - full_name_list_result: string[] 公司名称列表
    """
    data = pd.read_stata(filepath)
    # get column data
    code_list = [str(code).zfill(6)for code in data['stkcd']]  # 补零
    name_list = [name for name in data['name_simple']]
    full_name_list = [full_name for full_name in data['name']]
    return code_list, name_list, full_name_list


class ChromeBrowser():
    __browser = None

    def __init__(self) -> None:
        os.system("killall -9 'Google Chrome'")  # macos
        time.sleep(1)  # wait chrome exit
        option = webdriver.ChromeOptions()
        option.add_argument("start-maximized")
        option.add_argument(
            '--user-data-dir=/Users/xuejian/Library/Application Support/Google/Chrome/Default')  # macos
        self.__browser = webdriver.Chrome(options=option)

    def start_browser(self) -> None:
        """
        打开百度指数页面，等手动登录
        """
        self.__browser.get("https://index.baidu.com/v2/index.html")

    def input_and_search(self, keyword) -> None:
        """
        输入关键字并查询
        """
        "keyword-item__input"
        wait = WebDriverWait(self.__browser, 5)
        edit = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#search-input-form > input.search-input")))
        edit.send_keys(Keys.COMMAND+'a')  # slect all (cmd+a  for mac)
        edit.send_keys(Keys.BACKSPACE)  # delete
        edit.send_keys(keyword)
        submit = self.__browser.find_element(
            By.CLASS_NAME, "search-input-cancle")
        submit.click()
        pass


if __name__ == '__main__':
    # read keyword data
    code_list, name_list, full_name_list = read_keywords_by_dta(
        "/Users/xuejian/Downloads/百度指数关键词.dta")
    # start browser
    browser = ChromeBrowser()
    browser.start_browser()
    time.sleep(20)  # 手动登录，如果已登录，可以注释掉，选择全部
    count = 0
    for code in code_list:
        browser.input_and_search(code)
        time.sleep(2)  # 2s查一次
        count = count + 1
        print("NO.{} total:{}".format(count, len(code_list)))
