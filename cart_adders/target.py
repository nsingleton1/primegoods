import time
from playwright.sync_api import sync_playwright

def add_to_cart_target(url, product_name, storage_state_path="storage_state.json"):
    fallback_selectors = [
        "button[data-test='buy-now-button']",
        "button[data-test='addToCartButton']",
        "button:has-text('Add to cart')",
        "//button[contains(text(),'Add to cart')]"
    ]
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=storage_state_path)
        page = context.new_page()
        print(f"[INFO] Navigating to product page for {product_name}...")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"[ERROR] Page.goto failed: {e}")
            page.screenshot(path=f"goto_timeout_{product_name}.png")
            with open(f"goto_failure_{product_name}.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            browser.close()
            return False
        print("[INFO] User-Agent:", page.evaluate("() => navigator.userAgent"))
        time.sleep(5)
        clicked = False
        for selector in fallback_selectors:
            for attempt in range(3):
                try:
                    print(f"[TRY] Selector: {selector} (Attempt {attempt+1})")
                    locator = (
                        page.locator(f"xpath={selector}") if selector.startswith("//")
                        else page.locator(selector)
                    ).first
                    if locator.is_visible() and locator.is_enabled():
                        locator.scroll_into_view_if_needed()
                        locator.hover()
                        locator.click(delay=200)
                        locator.screenshot(path=f"button_match_{product_name}.png")
                        print(f"[SUCCESS] Clicked using selector: {selector}")
                        clicked = True
                        break
                except Exception as e:
                    print(f"[WARN] Attempt {attempt+1} failed for {selector}: {e}")
                    time.sleep(2)
            if clicked:
                break
        if not clicked:
            print(f"[FAIL] Could not click any Add to Cart button for {product_name}.")
            page.screenshot(path=f"cart_failure_{product_name}.png")
            with open(f"page_dump_{product_name}.html", "w", encoding="utf-8") as f:
                f.write(page.content())
        browser.close()
        return clicked 