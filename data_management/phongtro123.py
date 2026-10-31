import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ai_gemini import xu_ly_batch
from parsers import chuyen_gia_sang_int, chuyen_dien_tich_sang_real, lay_anh_carousel
from prompts import PROMPT_PHONGTRO123


def lay_card_o_trang_danh_sach(html):
    soup = BeautifulSoup(html, 'html.parser')
    ket_qua = []
    for the_a in soup.select('h3 a'):
        card = the_a.find_parent('li')
        if card is None:
            continue
        adr_tag = card.select_one('a.text-body[href*="/tinh-thanh/"]')
        # 'Hoài Đức, Hà Nội' -> 'Hoài Đức'
        huyen_quan = adr_tag.get_text(strip=True).split(',')[0].strip() if adr_tag else ""
        if not huyen_quan:
            continue
        url = the_a.get('href', '')
        if url and not url.startswith("http"):
            url = "https://phongtro123.com" + url
        ket_qua.append({"url": url, "tieu_de": the_a.get_text(strip=True), "huyen_quan": huyen_quan})
    return ket_qua


def doc_trang_chi_tiet(html):
    soup = BeautifulSoup(html, 'html.parser')

    gia_tag = soup.select_one('span.text-green.fs-5.fw-bold')
    gia = chuyen_gia_sang_int(gia_tag.get_text(strip=True)) if gia_tag else None

    dien_tich = next(
        (chuyen_dien_tich_sang_real(t) for t in
         (sp.get_text(" ", strip=True) for sp in soup.select('span:has(sup)'))
         if re.match(r'^\s*[\d.,]+\s*m', t)),
        None)

    dia_chi = ""
    for td in soup.select('td'):
        if td.get_text(strip=True).rstrip(':').strip().lower() == 'địa chỉ':
            td_ke = td.find_next_sibling('td')
            dia_chi = td_ke.get_text(" ", strip=True) if td_ke else ""
            break
    if not dia_chi:
        print("    ! Không tìm thấy địa chỉ chính xác")

    mo_ta = ""
    for h2 in soup.select('h2'):
        if 'Thông tin mô tả' in h2.get_text():
            mo_ta = "\n".join(p.get_text(" ", strip=True)
                              for p in h2.parent.select('p') if p.get_text(strip=True))
            break

    anh_urls = lay_anh_carousel(soup)
    if not anh_urls:
        og = soup.select_one('meta[property="og:image"]')
        if og and (og.get("content") or "").strip():
            anh_urls = [og["content"].strip()]

    return {"gia": gia, "dien_tich": dien_tich, "dia_chi_chinh_xac": dia_chi,
            "mo_ta": mo_ta, "anh_urls": anh_urls}


def gui_batch_phongtro123(batch):
    batch_ai = [{"url": b["url"], "tieu_de": b["tieu_de"], "thong_tin_them": b["mo_ta"]} for b in batch]
    batch_db = [{
        "url": b["url"],
        "dia_chi_cu": b["dia_chi_chinh_xac"],
        "dia_chi_moi": "", 
        "huyen_quan": b["huyen_quan"],
        "gia": b["gia"],
        "dien_tich": b["dien_tich"],
        "anh_urls": b.get("anh_urls") or [],
    } for b in batch]
    xu_ly_batch(batch_ai, batch_db, PROMPT_PHONGTRO123)


def ham_scrape_phongtro123_bam_card(url_goc, so_trang=3, batch_size=10):
    driver = webdriver.Chrome()
    da_gap = set()
    selector_card = "h3 a"

    def cho(css_hoac_xpath, by=By.CSS_SELECTOR):
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, css_hoac_xpath)))

    try:
        for trang in range(1, so_trang + 1):
            url_trang = url_goc if trang == 1 else f"{url_goc}?page={trang}"
            driver.get(url_trang)
            cho(selector_card)
            time.sleep(1.5)

            danh_sach_card = lay_card_o_trang_danh_sach(driver.page_source)
            print(f"\n=== Trang {trang}: {len(danh_sach_card)} card ===")

            batch = []
            for i, card in enumerate(danh_sach_card, 1):
                if card["url"] in da_gap:
                    continue
                da_gap.add(card["url"])

                da_roi_trang = False 
                try:
                    # tìm link theo đuôi href (slug) 
                    slug = card["url"].rstrip("/").split("/")[-1]
                    ds_link = driver.find_elements(By.CSS_SELECTOR, f'h3 a[href$="{slug}"]')

                    if ds_link:
                        link = ds_link[0]
                        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
                        time.sleep(0.5)
                        try:
                            link.click()
                        except Exception:
                            driver.execute_script("arguments[0].click();", link)
                    else:
                        print(f"  [{i}] Không thấy link, vào thẳng URL card")
                        driver.get(card["url"])
                    da_roi_trang = True

                    cho("span.text-green.fs-5.fw-bold")
                    for _ in range(4):
                        driver.execute_script("window.scrollBy(0, document.body.scrollHeight / 4);")
                        time.sleep(0.5)
                    try:
                        cho("//p[contains(., 'Địa chỉ')]", By.XPATH)
                    except Exception:
                        pass
                    time.sleep(1)

                    chi_tiet = doc_trang_chi_tiet(driver.page_source)
                    print(f"  [{i}/{len(danh_sach_card)}] {card['tieu_de'][:50]}")
                    batch.append({**card, **chi_tiet})

                except Exception as e:
                    print(f"  [{i}] Lỗi card {card['url']}: {e}")

                finally:
                    if da_roi_trang:
                        driver.back()
                    try:
                        cho(selector_card)
                    except Exception:
                        driver.get(url_trang)
                    time.sleep(1)

                if len(batch) == batch_size:
                    gui_batch_phongtro123(batch)
                    batch = []

            if batch:
                gui_batch_phongtro123(batch)
    finally:
        driver.quit()
