import os
import random
import time
from typing import Optional
from DrissionPage import Chromium, ChromiumOptions, ChromiumPage
from pathlib import Path
from .logu import logger
from DrissionPage._elements.chromium_element import ChromiumElement
def create_browser(address='127.0.0.1:19222', user_data_dir='', browser_path='', force_new=False):
    """
    创建浏览器连接，支持自动清理失效连接

    Args:
        address: 浏览器调试地址
        user_data_dir: 用户数据目录
        browser_path: 浏览器路径
        force_new: 是否强制创建新连接（不重用现有驱动）

    Returns:
        ChromiumPage 实例
    """
    from DrissionPage._base.chromium import Chromium
    from DrissionPage._pages.chromium_page import ChromiumPage

    chrome_options = ChromiumOptions(read_file=False)
    chrome_options.set_address(address)

    if user_data_dir:
        chrome_options.set_user_data_path(user_data_dir)
    if browser_path:
        chrome_options.set_browser_path(browser_path)

    try:
        # 创建浏览器连接
        driver = ChromiumPage(addr_or_opts=chrome_options)

        # 验证连接是否有效
        try:
            _ = driver.get_tabs()
            logger.debug(f"浏览器连接成功: {address}")
            return driver
        except Exception as e:
            error_msg = str(e)
            # 检查是否为连接断开错误
            is_disconnected = (
                "连接" in error_msg or
                "连接已断开" in error_msg or
                "connection" in error_msg.lower() or
                "disconnected" in error_msg.lower() or
                "Target closed" in error_msg or
                "Session not found" in error_msg or
                "_dl_mgr" in error_msg
            )

            if is_disconnected:
                logger.warning(f"检测到浏览器连接已断开: {error_msg}")

                # 手动清理 DrissionPage 的两个缓存
                browser_id = driver.browser.id if hasattr(driver, 'browser') and driver.browser else None
                if browser_id:
                    try:
                        logger.info(f"清理失效的浏览器缓存: browser_id={browser_id}")
                        Chromium._BROWSERS.pop(browser_id, None)
                        ChromiumPage._PAGES.pop(browser_id, None)
                        logger.info("缓存清理完成")
                    except Exception as cleanup_error:
                        logger.warning(f"清理缓存时出错: {cleanup_error}")

                # 等待一小段时间让资源释放
                time.sleep(0.5)

                # 尝试重新连接
                logger.info("尝试重新连接...")
                driver = ChromiumPage(addr_or_opts=chrome_options)
                _ = driver.get_tabs()
                logger.info("浏览器重新连接成功")
                return driver
            else:
                raise

    except Exception as e:
        error_msg = f"无法连接到浏览器 {address}: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

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
    page.get("chrome://version")
    print(page.browser._driver.address)
    
if __name__ == "__main__":
    main()