import json


def lay_so(text):
    try:
        return float(text.strip().replace(",", "."))
    except ValueError:
        return None


def phong_phu_hop(p, gia_max, quan, dt_min, dt_max, do_dung):
    if gia_max is not None and (p["gia"] is None or p["gia"] > gia_max):
        return False
    if quan:   
        dia_diem = " ".join(
            p[k] or "" for k in ("dia_chi_cu", "dia_chi_moi", "huyen_quan")
        ).casefold()
        if not any(q in dia_diem for q in quan):
            return False
    dt = p["dien_tich"]
    if dt_min is not None and (dt is None or dt < dt_min):
        return False
    if dt_max is not None and (dt is None or dt > dt_max):
        return False
    try:
        co = [x.casefold() for x in json.loads(p["do_dung_hien_co"] or "[]")]
    except (json.JSONDecodeError, TypeError):
        co = []
    return all(any(can.casefold() in x for x in co) for can in do_dung)
