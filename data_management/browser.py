import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

XPATH_NUT_XEM_THEM = (
    "//*[(self::button or self::a or self::div or self::span)"
    " and (contains(normalize-space(.), 'Xem thêm') or contains(normalize-space(.), 'Tải thêm'))"
    " and not(.//*[contains(normalize-space(.), 'Xem thêm') or contains(normalize-space(.), 'Tải thêm')])]"
)


def tim_nut(driver):
    ds_nut = [
        e for e in driver.find_elements(By.XPATH, XPATH_NUT_XEM_THEM)
        if e.is_displayed()
    ]
    if not ds_nut:
        return None
    return max(ds_nut, key=lambda e: e.location["y"])


def bam_nut(driver, nut):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", nut)
    time.sleep(0.5)
    try:
        nut.click()
    except Exception:
        driver.execute_script("arguments[0].click();", nut)


def dem_card(driver, selector):
    return len(driver.find_elements(By.CSS_SELECTOR, selector))


def tai_trang(url, so_lan_bam=4, selector_card=".c-sdb-card__tle",
              cho_max=15, so_thu=2):
    driver = webdriver.Chrome()
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            lambda d: d.find_elements(By.CSS_SELECTOR, selector_card)
        )

        so_card = dem_card(driver, selector_card)
        print(f"Ban đầu có {so_card} card.")

        for i in range(1, so_lan_bam + 1):
            da_tang = False

            for lan in range(1, so_thu + 1):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

                nut = tim_nut(driver)
                if nut is None:
                    print(f"Lần {i}: không thấy nút xem thêm (lần thử {lan}).")
                    time.sleep(2)
                    continue

                bam_nut(driver, nut)
                try:
                    WebDriverWait(driver, cho_max).until(
                        lambda d: dem_card(d, selector_card) > so_card
                    )
                    da_tang = True
                    break
                except Exception:
                    print(f"Lần {i}: đã bấm nhưng chưa có thêm card (lần thử {lan}).")

            so_moi = dem_card(driver, selector_card)
            if not da_tang:
                print(f"Dừng ở lần {i}: không tải thêm được (có thể đã hết bài). Tổng {so_moi} card.")
                break

            print(f"Đã bấm xem thêm lần {i}: {so_card} -> {so_moi} card.")
            so_card = so_moi
            time.sleep(1)

        return driver.page_source
    finally:
        driver.quit()
