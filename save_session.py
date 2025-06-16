from playwright.sync_api import sync_playwright

def save_target_session():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to Target and log in manually
        page.goto("https://www.target.com")

        input("[ACTION] Log in to Target in the opened browser. Press Enter here when finished.")

        # Save the logged-in session to a file
        context.storage_state(path="storage_state.json")
        print("[SUCCESS] Session saved to storage_state.json")

        browser.close()

if __name__ == "__main__":
    save_target_session()
