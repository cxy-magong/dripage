from utils.drission_page import create_browser
import sys
sys.executable
def main():
    page = create_browser()
    page.get("chrome://version")
    # ws://127.0.0.1:19222/devtools/browser/70f9d987-2e85-4000-a9e4-65e4580477f6
    print(page.browser._driver.address)
    
if __name__ == "__main__":
    main()