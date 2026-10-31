import json
import time

from google import genai

from config import GEMINI_API_KEY, GEMINI_MODEL
from database import ham_sqlite_luu_nhieu


def ham_ai_gemini(batch, prompt_template):
    client = genai.Client(api_key=GEMINI_API_KEY)
    du_lieu = [{k: b[k] for k in ("url", "tieu_de", "thong_tin_them")} for b in batch]

    prompt = prompt_template.replace("{du_lieu}", json.dumps(du_lieu, ensure_ascii=False, indent=2))
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL, contents=prompt,
            config={"response_mime_type": "application/json"})
        ket_qua = json.loads(response.text)
        if not isinstance(ket_qua, list):
            print("Gemini không trả về JSON ARRAY.")
            return []
        return ket_qua
    except Exception as e:
        print(f"====== API ERROR ======\n{e}\n=======")
        return []


def xu_ly_batch(batch_ai, batch_database, prompt_template):
    print(f"\nĐang gửi {len(batch_ai)} bài trong 1 request tới Gemini...")
    ai_results = ham_ai_gemini(batch_ai, prompt_template)
    time.sleep(4)
    if not ai_results:
        print("Gemini không trả về dữ liệu.")
        return

    ai_by_url = {r["url"]: r for r in ai_results if r.get("url")}
    data = []
    for bai in batch_database:
        ai = ai_by_url.get(bai["url"], {})
        data.append({
            **bai,
            "gia_dien": ai.get("gia_dien"),
            "gia_nuoc": ai.get("gia_nuoc"),
            "gia_dich_vu": ai.get("gia_dich_vu"),
            "do_dung_hien_co": ai.get("do_dung_hien_co") or [],
        })
    ham_sqlite_luu_nhieu(data)
    print(f"Đã lưu {len(data)} bài vào Database.")
