from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
import os
from datetime import datetime

def find_add_to_cart_button(page, log, product_name):
    # Try multiple strategies to find the Add to Cart button
    selectors = [
        "button[data-test='addToCartButton']",
        "button[data-test='orderPickupButton']",
        "button:has-text('Add to cart')",
    ]
    # Fallback: any button with 'add to cart' in its visible text (case-insensitive)
    def fallback_text_search():
        for btn in page.query_selector_all('button'):
            try:
                text = btn.inner_text().strip().lower()
                if 'add to cart' in text:
                    return btn
            except Exception:
                continue
        return None

    for selector in selectors:
        try:
            log(product_name, f"Trying selector: {selector}")
            btn = page.query_selector(selector)
            if btn and btn.is_visible() and btn.is_enabled():
                return btn
        except Exception:
            continue
    # Fallback: search all buttons for visible text
    log(product_name, "Trying fallback: any button with 'add to cart' in visible text")
    btn = fallback_text_search()
    if btn and btn.is_visible() and btn.is_enabled():
        return btn
    return None

def check_and_cart_product(url, selector, storage_state_path, log, product_name):
    if not os.path.exists(storage_state_path):
        raise FileNotFoundError(
            f"storage_state.json not found! Please run: playwright codegen target.com and log in."
        )
    screenshots_dir = 'screenshots'
    os.makedirs(screenshots_dir, exist_ok=True)
    ZIP_CODE = '10001'
    if 'zip=' not in url:
        url += ('&' if '?' in url else '?') + f'zip={ZIP_CODE}'
    for attempt in range(2):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(storage_state=storage_state_path)
            page = context.new_page()
            try:
                log(product_name, f"Loading page (attempt {attempt+1})...")
                page.goto(url, timeout=30000)
                page.wait_for_load_state('domcontentloaded')
                page.wait_for_load_state('networkidle')
                time.sleep(2)
                # Dismiss overlays/popups if present
                try:
                    close_btn = page.query_selector("button[aria-label='Close']")
                    if close_btn and close_btn.is_visible():
                        close_btn.click()
                        time.sleep(1)
                except Exception:
                    pass
                # Try to find the Add to Cart button
                log(product_name, "Looking for Add to Cart button...")
                button = find_add_to_cart_button(page, log, product_name)
                if button:
                    try:
                        log(product_name, "Add to Cart button found. Attempting click...")
                        button.click(timeout=5000)
                        time.sleep(1)
                        context.storage_state(path=storage_state_path)
                        page.close()
                        context.close()
                        browser.close()
                        return True
                    except Exception as e:
                        log(product_name, f"Click failed: {e}. Retrying once after wait...")
                        time.sleep(2)
                        button = find_add_to_cart_button(page, log, product_name)
                        if button:
                            button.click(timeout=5000)
                            time.sleep(1)
                            context.storage_state(path=storage_state_path)
                            page.close()
                            context.close()
                            browser.close()
                            return True
                        else:
                            log(product_name, "Button not clickable after retry.")
                # If we get here, button was not found or not clickable
                log(product_name, "Add to Cart button not found or not clickable. Saving screenshot.")
                screenshot_path = os.path.join(screenshots_dir, f"{product_name.replace(' ', '_')}.png")
                page.screenshot(path=screenshot_path, full_page=True)
            except Exception as e:
                log(product_name, f"Playwright error: {e}")
                screenshot_path = os.path.join(screenshots_dir, f"{product_name.replace(' ', '_')}_error.png")
                try:
                    page.screenshot(path=screenshot_path, full_page=True)
                except Exception:
                    pass
            finally:
                try:
                    page.close()
                    context.close()
                    browser.close()
                except Exception:
                    pass
        if attempt == 0:
            log(product_name, "Retrying after 3 seconds...")
            time.sleep(3)
    return False 