import json
import time

from google import genai

from config import GEMINI_API_KEY, GEMINI_MODEL
from database import luu_tro


def goi_gemini(batch, mau_prompt):
    client = genai.Client(api_key=GEMINI_API_KEY)
    du_lieu = [{k: b[k] for k in ("url", "tieu_de", "thong_tin_them")} for b in batch]
    prompt = mau_prompt.replace(
        "{du_lieu}", json.dumps(du_lieu, ensure_ascii=False, indent=2)
    )

    try:
        res = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        kq = json.loads(res.text)
        if not isinstance(kq, list):
            print("Gemini không trả về JSON ARRAY.")
            return []
        return kq
    except Exception as e:
        print(f"====== API ERROR ======\n{e}\n=======")
        return []


def xu_ly_batch(batch_ai, batch_db, mau_prompt):
    print(f"\nĐang gửi {len(batch_ai)} bài trong 1 request tới Gemini...")
    kq_ai = goi_gemini(batch_ai, mau_prompt)
    time.sleep(4)

    if not kq_ai:
        print("Gemini không trả về dữ liệu.")
        return

    ai_theo_url = {r["url"]: r for r in kq_ai if r.get("url")}
    ds_tro = []
    for bai in batch_db:
        ai = ai_theo_url.get(bai["url"], {})
        ds_tro.append({
            **bai,
            "gia_dien": ai.get("gia_dien"),
            "gia_nuoc": ai.get("gia_nuoc"),
            "gia_dich_vu": ai.get("gia_dich_vu"),
            "do_dung_hien_co": ai.get("do_dung_hien_co") or [],
        })

    luu_tro(ds_tro)
    print(f"Đã lưu {len(ds_tro)} bài vào Database.")
