from playwright.sync_api import sync_playwright
import time
from cart_adders.target import add_to_cart_target

def run_cart_attempt():
    product_url = "https://www.target.com/p/keurig-k-mini-single-serve-k-cup-pod-coffee-maker/-/A-53788870"
    fallback_selectors = [
        "button[data-test='buy-now-button']",
        "button[data-test='addToCartButton']",
        "button:has-text('Add to cart')",
        "//button[contains(text(),'Add to cart')]"
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="storage_state.json")
        page = context.new_page()

        print("[INFO] Navigating to product page...")
        try:
            page.goto(product_url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"[ERROR] Page.goto failed: {e}")
            page.screenshot(path="goto_timeout.png")
            with open("goto_failure.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            browser.close()
            return

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
                        locator.screenshot(path="button_match.png")
                        print(f"[SUCCESS] Clicked using selector: {selector}")
                        clicked = True
                        break
                except Exception as e:
                    print(f"[WARN] Attempt {attempt+1} failed for {selector}: {e}")
                    time.sleep(2)
            if clicked:
                break

        if not clicked:
            print("[FAIL] Could not click any Add to Cart button.")
            page.screenshot(path="cart_failure.png")
            with open("page_dump.html", "w", encoding="utf-8") as f:
                f.write(page.content())

        browser.close()

if __name__ == "__main__":
    # Example usage for manual testing
    url = "https://www.target.com/p/keurig-k-mini-single-serve-k-cup-pod-coffee-maker/-/A-53788870"
    product_name = "Keurig K-Mini Single-Serve Coffee Maker"
    added = add_to_cart_target(url, product_name)
    if added:
        print(f"[TEST] {product_name} was added to cart!")
    else:
        print(f"[TEST] {product_name} could NOT be added to cart.")
