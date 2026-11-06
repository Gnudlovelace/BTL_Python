import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def doc_so(s):
    return float(s.replace(",", "."))


def doc_gia(gia):
    gia = gia.lower().strip()
    for mau, he_so in ((r"([\d.,]+)\s*triệu", 1_000_000), (r"([\d.,]+)\s*(?:k|nghìn)", 1_000)):
        m = re.search(mau, gia)
        if m:
            return int(round(doc_so(m.group(1)) * he_so))
    return None


def doc_dien_tich(dien_tich):
    m = re.search(r"([\d.,]+)", dien_tich)
    return doc_so(m.group(1)) if m else None


def tach_quan(dia_chi):
    if not dia_chi:
        return ""

    cac_phan = [p.strip() for p in dia_chi.split(",") if p.strip()]

    for phan in cac_phan:
        if re.search(r"\b(quận|huyện|thị xã|thành phố)\b", phan, re.I):
            return re.sub(
                r"^\s*(?:quận|huyện|thị xã|thành phố)\s*", "", phan, flags=re.I
            ).strip()

    for phan in cac_phan:
        m = re.search(r"^\s*(?:q|h|tx)\.?\s*(.+)", phan, re.I)
        if m:
            return m.group(1).strip()

    return ""


def tach_dia_chi(card):
    dia_chi_cu = dia_chi_moi = ""
    for adr in card.select(".sdb-inf-data.data-type-adr"):
        text = adr.get_text(" ", strip=True)
        if "(Mới)" in text:
            dia_chi_moi = text.replace("(Mới)", "").strip()
        else:
            dia_chi_cu = text
    return dia_chi_cu, dia_chi_moi


def lay_text(node, selector):
    tag = node.select_one(selector)
    return tag.get_text(strip=True) if tag else ""


def them_url(ds, url):
    if url and url not in ds:
        ds.append(url)


def lay_anh_guland(html, goc="https://guland.vn"):
    soup = html if hasattr(html, "select") else BeautifulSoup(html, "html.parser")

    ds = []
    for el in soup.select(".media-thumb-wrap__inner"):
        m = re.search(r"url\(\s*(['\"]?)(.*?)\1\s*\)", el.get("style") or "")
        if m:
            them_url(ds, urljoin(goc, m.group(2).strip()))

    nhom = {}
    for u in ds:
        m = re.search(r"/posts/(\d+)/", u)
        nhom.setdefault(m.group(1) if m else None, []).append(u)

    if len(nhom) <= 1:
        return ds
    return max(nhom.values(), key=len)


def lay_anh_phongtro(html, goc="https://phongtro123.com"):
    soup = html if hasattr(html, "select") else BeautifulSoup(html, "html.parser")
    carousel = soup.select_one(".carousel-inner.bg-dark") or soup.select_one(".carousel-inner")

    ds = []
    for img in carousel.select("img") if carousel is not None else []:
        for attr in ("data-src", "data-original", "src"):
            v = (img.get(attr) or "").strip()
            if v and not v.startswith("data:"):
                them_url(ds, urljoin(goc, v))
                break
    return ds
