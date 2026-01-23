#!/usr/bin/env python
"""
Action function implementation for DrissionPage browser control
Performs right-click at coordinates (300, 300) using tab.action from page.latest_tab
"""
import time

from utils.drission_page import create_browser


def action():
    """
    Connect to default browser and perform right-click at coordinates (300, 300)
    using tab.action from page.latest_tab

    Returns:
        ChromiumPage: The page object for further operations
    """
    # Create browser connection
    page = create_browser()

    # Get the latest tab
    tab = page.latest_tab
    print(tab.title)
    # Perform right-click at coordinates (300, 300)
    tab.actions.move_to((217, 274))
    time.sleep(1)
    tab.actions.r_click()
    # tab.actions.click()
    return page


if __name__ == "__main__":
    action()
