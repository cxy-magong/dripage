import os
import random
import time
from typing import Optional
from DrissionPage import Chromium, ChromiumOptions, ChromiumPage
from pathlib import Path
from .logu import logger
from DrissionPage._elements.chromium_element import ChromiumElement
def create_browser(address='127.0.0.1:19222', user_data_dir='', browser_path=''):

    chrome_options = ChromiumOptions(read_file=False)
    # 务必不能小于10000，否则可能由于环境问题导致错误
    chrome_options.set_address(address)
    if user_data_dir:
        chrome_options.set_user_data_path(user_data_dir)
    if browser_path:
        chrome_options.set_browser_path(browser_path)
    driver = ChromiumPage(addr_or_opts=chrome_options)
    return driver

def create_temp_browser():
    driver = ChromiumPage()
    return driver


def click_random_pos(ele:ChromiumElement, delay_random=(0,5), safe_zone=0.2, wait_timeout=35):

    """在元素中心区域随机点击
    
    Args:
        ele: 要点击的元素
        delay_random: 点击前的随机延迟时间范围（秒）
        safe_zone: 安全区域比例，0.2表示在中心80%区域内随机点击
        wait_timeout: 等待元素出现并具有可点击矩形区域的超时时间（秒）
    """
    # 等待元素出现并具有可点击的矩形区域
    logger.debug(f"等待元素出现并具有可点击矩形区域，超时时间：{wait_timeout}秒")
    ele.wait.has_rect(timeout=wait_timeout)
    
    # 获取元素大小和位置信息
    width, height = ele.rect.size
    logger.debug(f"元素大小：{width}x{height}")
    center_x, center_y = width/2, height/2
    
    max_offset_x = width * safe_zone
    max_offset_y = height * safe_zone
    
    # 在中心点附近生成随机偏移量
    offset_x = center_x + random.uniform(-max_offset_x, max_offset_x)
    offset_y = center_y + random.uniform(-max_offset_y, max_offset_y)
    logger.debug(f"中心点：{center_x},{center_y}")
    logger.debug(f"偏移量：{offset_x},{offset_y}")
    # 执行带偏移量的点击
    time.sleep(random.uniform(*delay_random))
    ele.click.at(offset_x, offset_y)

def find_and_click_random(driver:ChromiumElement|ChromiumPage, locator, *args, **kwargs):
    """查找元素并随机点击
    
    Args:
        driver: 浏览器驱动或元素
        locator: 元素定位器
        *args: 传递给 ele() 方法的位置参数
        **kwargs: 传递给 click_random_pos() 方法的关键字参数
    """
    ele = driver.ele(locator, *args)
    return click_random_pos(ele, **kwargs)

def main():
    page = create_browser()
    page._driver._websocket_url
    page.get("chrome://version")
    print(page._driver._websocket_url)
    
if __name__ == "__main__":
    main()