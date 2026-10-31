import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from ai_gemini import xu_ly_batch
from parsers import (chuyen_gia_sang_int, chuyen_dien_tich_sang_real,
                     tach_huyen_quan, tach_dia_chi, lay_anh_guland, _text)
from prompts import PROMPT_GULAND

SELECTOR_ANH = ".media-thumb-wrap__inner"


def lay_anh_trong_card(driver, url):
    try:
        driver.get(url)
        try:
            WebDriverWait(driver, 8).until(
                lambda d: d.find_elements(By.CSS_SELECTOR, SELECTOR_ANH))
        except Exception:
            pass                     
        time.sleep(1)                 
        return lay_anh_guland(driver.page_source)
    except Exception as e:
        print(f"    ! Lỗi lấy ảnh {url}: {e}")
        return []


def doc_danh_sach_card(html):
    """Đọc trang danh sách -> [(dữ liệu gửi AI, dữ liệu lưu DB)] đã bỏ trùng / thiếu quận."""
    soup = BeautifulSoup(html, 'html.parser')
    ket_qua, da_gap = [], set()
    bo_qua_trung = bo_qua_thieu_quan = 0

    tieu_de_tags = soup.select('.c-sdb-card__tle')
    print(f"Tìm thấy {len(tieu_de_tags)} card trong HTML guland.")

    for tieu_de_tag in tieu_de_tags:
        card = (tieu_de_tag.find_parent('div', class_=re.compile('card|item|box', re.I))
                or tieu_de_tag.parent.parent)

        the_a = tieu_de_tag.find('a')
        url = the_a.get('href', '') if the_a else ''
        if url and not url.startswith("http"):
            url = "https://guland.vn" + url

        if url in da_gap:
            bo_qua_trung += 1
            continue

        dia_chi_cu, dia_chi_moi = tach_dia_chi(card)
        huyen_quan = tach_huyen_quan(dia_chi_cu)
        if not huyen_quan:
            bo_qua_thieu_quan += 1
            continue
        da_gap.add(url)

        ket_qua.append(({
            "url": url,
            "tieu_de": tieu_de_tag.get_text(strip=True),
            "thong_tin_them": _text(card, '.c-sdb-card__exc'),
        }, {
            "url": url,
            "dia_chi_cu": dia_chi_cu,
            "dia_chi_moi": dia_chi_moi,
            "huyen_quan": huyen_quan,
            "anh_urls": [],
            "gia": chuyen_gia_sang_int(_text(card, '.sdb-inf-data.data-color-1.data-size-xl')),
            "dien_tich": chuyen_dien_tich_sang_real(_text(card, '.sdb-inf-data.data-size-lg b')),
        }))

    print(f"Guland: giữ {len(ket_qua)} bài | bỏ qua {bo_qua_trung} trùng, "
          f"{bo_qua_thieu_quan} không tách được quận/huyện.")
    return ket_qua


def ham_rieng_scraping_guland(html, batch_size=10):
    cac_card = doc_danh_sach_card(html)
    if not cac_card:
        return

    driver = webdriver.Chrome()
    batch_ai, batch_db = [], []
    try:
        for i, (ai, db) in enumerate(cac_card, 1):
            db["anh_urls"] = lay_anh_trong_card(driver, db["url"])
            print(f"  [{i}/{len(cac_card)}] {ai['tieu_de'][:50]} -> {len(db['anh_urls'])} ảnh")
            batch_ai.append(ai)
            batch_db.append(db)

            if len(batch_ai) == batch_size:
                xu_ly_batch(batch_ai, batch_db, PROMPT_GULAND)
                batch_ai, batch_db = [], []
        if batch_ai:
            xu_ly_batch(batch_ai, batch_db, PROMPT_GULAND)
    finally:
        driver.quit()
