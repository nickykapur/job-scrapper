#!/usr/bin/env python3
"""
Test script to debug LinkedIn Easy Apply detection
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
import time

def test_easy_apply_detection():
    """Test Easy Apply detection on a live LinkedIn job search"""

    # Setup Chrome in headless mode
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Search for software jobs with Easy Apply filter
        # f_AL=true is the URL parameter for Easy Apply filter
        url = "https://www.linkedin.com/jobs/search?keywords=software%20engineer&location=Ireland&f_TPR=r86400&f_AL=true&position=1&pageNum=0"

        print(f"Opening LinkedIn job search with Easy Apply filter...")
        driver.get(url)
        time.sleep(5)

        # Wait for job cards to load
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".job-search-card, .base-card, .job-result-card"))
            )
            print("✅ Job cards loaded")
        except:
            print("❌ No job cards found")
            return

        time.sleep(3)

        # Find all job cards
        selectors = [".job-search-card", ".base-card", ".job-result-card", "[data-entity-urn*='job']"]
        job_cards = []

        for selector in selectors:
            cards = driver.find_elements(By.CSS_SELECTOR, selector)
            if cards:
                job_cards = cards
                print(f"✅ Found {len(cards)} job cards using selector: {selector}")
                break

        if not job_cards:
            print("❌ No job cards found with any selector")
            return

        # Analyze first 3 job cards
        print(f"\n{'='*80}")
        print("Analyzing Easy Apply detection on job cards:")
        print(f"{'='*80}\n")

        for idx, card in enumerate(job_cards[:3], 1):
            try:
                # Get job title
                title = "Unknown"
                title_selectors = [
                    ".base-search-card__title",
                    ".job-search-card__title",
                    "h3"
                ]
                for sel in title_selectors:
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, sel)
                        title = title_elem.text.strip()
                        if title:
                            break
                    except:
                        continue

                print(f"\n--- Job Card #{idx}: {title} ---")

                # Get the card's full text content
                card_text = card.text.lower()
                print(f"Card text contains 'easy apply': {'easy apply' in card_text}")
                print(f"Card text contains 'solicitud sencilla': {'solicitud sencilla' in card_text}")

                # Test all possible Easy Apply selectors
                test_selectors = [
                    ".job-search-card__easy-apply-label",
                    "[aria-label*='Easy Apply']",
                    "[aria-label*='easy apply']",
                    ".artdeco-entity-lockup__badge--easy-apply",
                    "li-icon[type='easy-apply-logo']",
                    ".job-card-list__easy-apply",
                    ".job-card-container__apply-method",
                    "[class*='easy-apply']",
                    "[class*='easy_apply']",
                    ".base-search-card__metadata",
                    ".job-search-card__job-insight",
                    ".job-card-container__footer-item"
                ]

                found_selectors = []
                for selector in test_selectors:
                    try:
                        elements = card.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            for elem in elements:
                                elem_text = elem.text.lower()
                                elem_html = elem.get_attribute('outerHTML')[:200]
                                if 'easy' in elem_text or 'easy' in elem_html.lower():
                                    found_selectors.append({
                                        'selector': selector,
                                        'text': elem_text,
                                        'visible': elem.is_displayed(),
                                        'html': elem_html
                                    })
                    except:
                        continue

                if found_selectors:
                    print(f"✅ Found {len(found_selectors)} matching elements:")
                    for match in found_selectors:
                        print(f"  - Selector: {match['selector']}")
                        print(f"    Text: '{match['text']}'")
                        print(f"    Visible: {match['visible']}")
                        print(f"    HTML: {match['html']}")
                else:
                    print("❌ No Easy Apply indicators found with tested selectors")

                    # Print the full card HTML for inspection (first 1000 chars)
                    card_html = card.get_attribute('outerHTML')
                    print(f"\nCard HTML sample (first 1000 chars):")
                    print(card_html[:1000])

                print()

            except Exception as e:
                print(f"❌ Error analyzing card #{idx}: {e}")
                continue

        print(f"\n{'='*80}")
        print("RECOMMENDATIONS:")
        print(f"{'='*80}")

        # Provide recommendations based on findings
        print("\nBased on this analysis:")
        print("1. Check if Easy Apply jobs are correctly filtered in the search URL")
        print("2. Verify if Easy Apply indicator appears in the card text")
        print("3. Consider that Easy Apply might only be visible on the detail page")
        print("4. LinkedIn may load Easy Apply badges dynamically after initial page load")

    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_easy_apply_detection()
