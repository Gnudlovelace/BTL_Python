import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from ai_gemini import xu_ly_batch
from parsers import (doc_gia, doc_dien_tich, tach_quan, tach_dia_chi,
                     lay_anh_guland, lay_text)
from prompts import PROMPT_GULAND

SELECTOR_ANH = ".media-thumb-wrap__inner"


def lay_anh_bai(driver, url):
    try:
        driver.get(url)
        try:
            WebDriverWait(driver, 8).until(
                lambda d: d.find_elements(By.CSS_SELECTOR, SELECTOR_ANH)
            )
        except Exception:
            pass
        time.sleep(1)
        return lay_anh_guland(driver.page_source)
    except Exception as e:
        print(f"    ! Lỗi lấy ảnh {url}: {e}")
        return []


def doc_danh_sach(html):
    soup = BeautifulSoup(html, "html.parser")
    kq, da_gap = [], set()
    so_trung = so_thieu_quan = 0

    ds_tieu_de = soup.select(".c-sdb-card__tle")
    print(f"Tìm thấy {len(ds_tieu_de)} card trong HTML guland.")

    for tieu_de in ds_tieu_de:
        card = (
            tieu_de.find_parent("div", class_=re.compile("card|item|box", re.I))
            or tieu_de.parent.parent
        )

        a = tieu_de.find("a")
        url = a.get("href", "") if a else ""
        if url and not url.startswith("http"):
            url = "https://guland.vn" + url

        if url in da_gap:
            so_trung += 1
            continue

        dia_chi_cu, dia_chi_moi = tach_dia_chi(card)
        quan = tach_quan(dia_chi_cu)
        if not quan:
            so_thieu_quan += 1
            continue
        da_gap.add(url)

        bai_ai = {
            "url": url,
            "tieu_de": tieu_de.get_text(strip=True),
            "thong_tin_them": lay_text(card, ".c-sdb-card__exc"),
        }
        bai_db = {
            "url": url,
            "dia_chi_cu": dia_chi_cu,
            "dia_chi_moi": dia_chi_moi,
            "huyen_quan": quan,
            "anh_urls": [],
            "gia": doc_gia(lay_text(card, ".sdb-inf-data.data-color-1.data-size-xl")),
            "dien_tich": doc_dien_tich(lay_text(card, ".sdb-inf-data.data-size-lg b")),
        }
        kq.append((bai_ai, bai_db))

    print(
        f"Guland: giữ {len(kq)} bài | bỏ qua {so_trung} trùng, "
        f"{so_thieu_quan} không tách được quận/huyện."
    )
    return kq


def cao_guland(html, batch_size=10):
    ds_bai = doc_danh_sach(html)
    if not ds_bai:
        return

    driver = webdriver.Chrome()
    batch_ai, batch_db = [], []
    try:
        for i, (bai_ai, bai_db) in enumerate(ds_bai, 1):
            bai_db["anh_urls"] = lay_anh_bai(driver, bai_db["url"])
            print(f"  [{i}/{len(ds_bai)}] {bai_ai['tieu_de'][:50]} -> {len(bai_db['anh_urls'])} ảnh")

            batch_ai.append(bai_ai)
            batch_db.append(bai_db)

            if len(batch_ai) == batch_size:
                xu_ly_batch(batch_ai, batch_db, PROMPT_GULAND)
                batch_ai, batch_db = [], []

        if batch_ai:
            xu_ly_batch(batch_ai, batch_db, PROMPT_GULAND)
    finally:
        driver.quit()
