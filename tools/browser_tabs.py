#!/usr/bin/env python
"""
Browser tab management tools for DrissionPage.
Enhanced with error handling, logging, and additional features.
"""
from typing import List, Optional, Literal
from utils.drission_page import create_browser
from utils.logu import logger


def get_browser():
    """Get browser instance."""
    return create_browser()


def list_tabs() -> str:
    """List all browser tabs.

    Returns:
        JSON string with list of tabs including their titles and URLs
    """
    import json
    try:
        logger.info("Listing all browser tabs")
        browser = get_browser()
        tabs = browser.get_tabs()

        logger.debug(f"Found {len(tabs)} tabs")

        tab_info = []
        current_tab = browser.get_tab()

        for i, tab in enumerate(tabs):
            try:
                tab_data = {
                    "index": i,
                    "title": tab.title,
                    "url": tab.url,
                    "is_current": tab == current_tab
                }
                tab_info.append(tab_data)
                logger.debug(f"Tab {i}: {tab.title} - {tab.url}")
            except Exception as e:
                logger.warning(f"Failed to get info for tab {i}: {e}")
                tab_info.append({
                    "index": i,
                    "title": "N/A",
                    "url": "N/A",
                    "is_current": tab == current_tab
                })

        result = json.dumps({
            "status": "success",
            "tabs": tab_info,
            "count": len(tab_info)
        }, ensure_ascii=False, indent=2)

        logger.info(f"Successfully listed {len(tab_info)} tabs")
        return result

    except Exception as e:
        logger.error(f"Failed to list tabs: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to list tabs: {str(e)}"
        }, ensure_ascii=False)


def switch_tab(tab_index: int) -> str:
    """Switch to a specific tab by index.

    Args:
        tab_index: The index of tab to switch to (0-based)

    Returns:
        Success message with new tab title and URL
    """
    import json
    try:
        logger.info(f"Switching to tab {tab_index}")
        browser = get_browser()
        tabs = browser.get_tabs()

        if tab_index < 0 or tab_index >= len(tabs):
            error_msg = f"Tab index {tab_index} out of range. Total tabs: {len(tabs)}"
            logger.error(error_msg)
            return json.dumps({
                "status": "error",
                "message": error_msg,
                "available_indices": list(range(len(tabs)))
            }, ensure_ascii=False)

        # Switch to tab using browser.activate_tab()
        # DrissionPage has activate_tab() method on browser level
        browser.activate_tab(tab_index)
        logger.info(f"Switched to tab {tab_index}")

        # Get current tab info after switching
        current_tab = browser.get_tab()

        result = json.dumps({
            "status": "success",
            "message": f"Switched to tab {tab_index}",
            "index": tab_index,
            "title": current_tab.title,
            "url": current_tab.url,
            "total_tabs": len(tabs)
        }, ensure_ascii=False, indent=2)

        logger.info(f"Successfully switched to: {current_tab.title}")
        return result

    except Exception as e:
        logger.error(f"Failed to switch tab: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to switch tab: {str(e)}"
        }, ensure_ascii=False)

        # Switch to tab using the tab object
        # DrissionPage doesn't have to_tab on browser level,
        # but we can switch using the tab reference
        target_tab = tabs[tab_index]
        target_tab.activate()
        logger.info(f"Switched to tab {tab_index}")

        # Get current tab info after switching
        current_tab = browser.get_tab()

        result = json.dumps({
            "status": "success",
            "message": f"Switched to tab {tab_index}",
            "index": tab_index,
            "title": current_tab.title,
            "url": current_tab.url,
            "total_tabs": len(tabs)
        }, ensure_ascii=False, indent=2)

        logger.info(f"Successfully switched to: {current_tab.title}")
        return result

    except Exception as e:
        logger.error(f"Failed to switch tab: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to switch tab: {str(e)}"
        }, ensure_ascii=False)

        # Switch to the tab
        browser.to_tab(tab_index)
        logger.info(f"Switched to tab {tab_index}")

        # Get current tab info
        current_tab = browser.get_tab()

        result = json.dumps({
            "status": "success",
            "message": f"Switched to tab {tab_index}",
            "index": tab_index,
            "title": current_tab.title,
            "url": current_tab.url,
            "total_tabs": len(tabs)
        }, ensure_ascii=False, indent=2)

        logger.info(f"Successfully switched to: {current_tab.title}")
        return result

    except Exception as e:
        logger.error(f"Failed to switch tab: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to switch tab: {str(e)}"
        }, ensure_ascii=False)


def new_tab(url: Optional[str] = None) -> str:
    """Open a new tab.

    Args:
        url: Optional URL to navigate to in the new tab

    Returns:
        Success message with the new tab title and URL
    """
    import json
    import time
    try:
        url_info = f" with URL: {url}" if url else ""
        logger.info(f"Opening new tab{url_info}")
        browser = get_browser()

        # Get tab count before opening
        previous_count = len(browser.get_tabs())
        logger.debug(f"Tab count before: {previous_count}")

        # Open new tab
        browser.new_tab(url)
        logger.debug("New tab created")

        # Small delay to allow tab to initialize
        time.sleep(0.5)

        # Get the new tab info
        new_tab = browser.get_tab()
        new_tab_index = browser.get_tabs().index(new_tab)

        logger.debug(f"New tab index: {new_tab_index}")

        result = json.dumps({
            "status": "success",
            "message": "New tab opened",
            "index": new_tab_index,
            "title": new_tab.title,
            "url": new_tab.url,
            "total_tabs": len(browser.get_tabs())
        }, ensure_ascii=False, indent=2)

        logger.info(f"Successfully opened new tab: {new_tab.title} - {new_tab.url}")
        return result

    except Exception as e:
        logger.error(f"Failed to open new tab: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to open new tab: {str(e)}"
        }, ensure_ascii=False)


def close_tab(tab_index: Optional[int] = None) -> str:
    """Close a tab.

    Args:
        tab_index: The index of tab to close (0-based).
                   If not provided, closes the current tab.

    Returns:
        Success message
    """
    import json
    import time
    try:
        logger.info(f"Closing tab{f' at index {tab_index}' if tab_index is not None else ' (current tab)'}")
        browser = get_browser()
        tabs = browser.get_tabs()

        # Check if we have at least one tab
        if len(tabs) == 0:
            logger.error("No tabs to close")
            return json.dumps({
                "status": "error",
                "message": "No tabs to close"
            }, ensure_ascii=False)

        if tab_index is None:
            # Close current tab using browser method
            # DrissionPage has close_tab() method on browser level
            # or we can close the current tab object directly
            current_tab = browser.get_tab()
            if current_tab:
                current_tab.close()
            logger.info("Current tab closed")

            # Small delay to allow browser to update
            time.sleep(0.3)

            # Get current tab info after closing
            current_tab = browser.get_tab()
            remaining_tabs = len(browser.get_tabs())

            result = json.dumps({
                "status": "success",
                "message": "Current tab closed",
                "current_tab_title": current_tab.title if current_tab else "N/A",
                "current_tab_url": current_tab.url if current_tab else "N/A",
                "remaining_tabs": remaining_tabs
            }, ensure_ascii=False, indent=2)

            logger.info(f"Successfully closed current tab. {remaining_tabs} tabs remaining")
            return result
        else:
            # Close specific tab
            if tab_index < 0 or tab_index >= len(tabs):
                error_msg = f"Tab index {tab_index} out of range. Total tabs: {len(tabs)}"
                logger.error(error_msg)
                return json.dumps({
                    "status": "error",
                    "message": error_msg,
                    "available_indices": list(range(len(tabs)))
                }, ensure_ascii=False)

            # Activate the tab first, then close it
            browser.activate_tab(tab_index)
            target_tab = browser.get_tab()

            if target_tab:
                target_tab.close()
            logger.info(f"Tab {tab_index} closed")

            # Small delay to allow browser to update
            time.sleep(0.3)

            # Get current tab info after closing
            current_tab = browser.get_tab()
            remaining_tabs = len(browser.get_tabs())

            result = json.dumps({
                "status": "success",
                "message": f"Tab {tab_index} closed",
                "current_tab_title": current_tab.title if current_tab else "N/A",
                "current_tab_url": current_tab.url if current_tab else "N/A",
                "remaining_tabs": remaining_tabs
            }, ensure_ascii=False, indent=2)

            logger.info(f"Successfully closed tab {tab_index}. {remaining_tabs} tabs remaining")
            return result

    except Exception as e:
        logger.error(f"Failed to close tab: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to close tab: {str(e)}"
        }, ensure_ascii=False)


def get_current_tab_info() -> str:
    """Get information about the current tab.

    Returns:
        JSON string with current tab title and URL
    """
    import json
    try:
        logger.info("Getting current tab info")
        browser = get_browser()
        current_tab = browser.get_tab()

        if not current_tab:
            logger.warning("No current tab found")
            return json.dumps({
                "status": "error",
                "message": "No current tab found"
            }, ensure_ascii=False)

        tabs = browser.get_tabs()
        current_index = tabs.index(current_tab)

        result = json.dumps({
            "status": "success",
            "index": current_index,
            "title": current_tab.title,
            "url": current_tab.url,
            "total_tabs": len(tabs)
        }, ensure_ascii=False, indent=2)

        logger.info(f"Current tab: {current_tab.title} at index {current_index}")
        return result

    except ValueError:
        logger.error("Current tab not found in tabs list")
        return json.dumps({
            "status": "error",
            "message": "Current tab not found in tabs list"
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to get current tab info: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Failed to get current tab info: {str(e)}"
        }, ensure_ascii=False)
