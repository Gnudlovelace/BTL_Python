import json
import re
import time

from .cau_hinh import (
    GEMINI_API_KEY, GEMINI_MODEL, DANH_SACH_QUAN_HUYEN, DANH_SACH_DO_DUNG,
    NGUONG_RE, NGUONG_RONG, NGUONG_NHO, TU_KHOA_MO_HO, TU_KHOA_DO_DUNG,
)
from .xu_ly_van_ban import chuan_ten, them, bo_dau, tim_quan


def tieu_chi_moi():
    return {
        "quan_huyen": [],
        "gia_max": None,
        "dien_tich_min": None,
        "dien_tich_max": None,
        "do_dung": [],
        "suy_luan": [],
        "canh_bao": [],
    }


def ep_so(gia_tri, kieu):
    try:
        return kieu(gia_tri) if gia_tri is not None else None
    except (TypeError, ValueError):
        return None


class ChatbotManager:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model or GEMINI_MODEL
        self.client = None

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[Chatbot] Không khởi tạo được Gemini: {e}")
                self.client = None

    def hoi_gemini(self, cau):
        if self.client is None:
            return None

        prompt = f"""
Bạn là trợ lý phân tích yêu cầu tìm phòng trọ tại Hà Nội.
Đọc câu của người dùng và trích xuất thành JSON với các khóa sau:
"quan_huyen": mảng tên quận/huyện phù hợp, CHỈ được chọn trong danh sách:
{json.dumps(DANH_SACH_QUAN_HUYEN, ensure_ascii=False)}.
  - Nếu người dùng nêu trực tiếp quận/huyện thì lấy đúng các quận/huyện đó.
  - Nếu người dùng nêu một địa điểm (trường học, tòa nhà, khu vực, địa danh...)
    kèm từ như "gần", "quanh", "cạnh" thì trả về quận/huyện chứa địa điểm đó
    và các quận/huyện lân cận gần nhất (tối đa 4). Ví dụ "gần Học viện Bưu chính
    Viễn thông" -> ["Hà Đông", "Thanh Xuân", "Nam Từ Liêm"].
  - Không có thông tin địa điểm -> [].
"gia_max": số nguyên VNĐ/tháng (ví dụ "dưới 3 triệu" -> 3000000), không có thì null.
  - Nếu người dùng nêu con số cụ thể thì dùng đúng con số đó.
  - Nếu chỉ dùng từ mô tả mơ hồ về giá như "rẻ", "giá rẻ", "bình dân", "tiết kiệm",
    "sinh viên" thì đặt {NGUONG_RE}.
"dien_tich_min": số m2 nhỏ nhất, không có thì null.
  - Nếu chỉ dùng từ mô tả như "rộng", "rộng rãi", "thoáng" thì đặt {NGUONG_RONG}.
"dien_tich_max": số m2 lớn nhất, không có thì null.
  - Nếu chỉ dùng từ mô tả như "nhỏ", "nhỏ gọn" thì đặt {NGUONG_NHO}.
"do_dung": mảng, chỉ chọn trong {json.dumps(DANH_SACH_DO_DUNG, ensure_ascii=False)}; không có thì [].

Lưu ý: hãy suy luận ý nghĩa của các tính từ/cụm từ trong câu để điền bộ lọc,
không chỉ tìm các giá trị được viết trực tiếp. Địa điểm như trường đại học, bệnh viện,
tòa nhà, khu đô thị... đều phải quy ra quận/huyện chứa nó và các quận/huyện lân cận.

Yêu cầu người dùng: "{cau}"

CHỈ TRẢ VỀ MỘT ĐỐI TƯỢNG JSON HỢP LỆ, KHÔNG GIẢI THÍCH, KHÔNG DÙNG MARKDOWN.
"""
        for lan in range(1, 3):
            try:
                kq = self.client.models.generate_content(
                    model=self.model, contents=prompt
                )
                return kq.text
            except Exception as e:
                print(f"[Chatbot] Gemini lần {lan} lỗi: {e}")
                if lan < 2:
                    time.sleep(1)
        return None

    def doc_json(self, raw):
        if not raw:
            return None
        try:
            sach = re.sub(r"```(?:json)?", "", raw, flags=re.IGNORECASE).strip()
            m = re.search(r"\{.*\}", sach, flags=re.DOTALL)
            data = json.loads(m.group(0) if m else sach)
        except Exception:
            return None

        tc = tieu_chi_moi()
        for q in data.get("quan_huyen") or []:
            them(tc["quan_huyen"], chuan_ten(q, DANH_SACH_QUAN_HUYEN))
        for d in data.get("do_dung") or []:
            them(tc["do_dung"], chuan_ten(d, DANH_SACH_DO_DUNG))

        tc["gia_max"] = ep_so(data.get("gia_max"), int)
        tc["dien_tich_min"] = ep_so(data.get("dien_tich_min"), float)
        tc["dien_tich_max"] = ep_so(data.get("dien_tich_max"), float)
        return tc

    def phan_tich(self, cau):
        msg = cau.casefold()
        tc = tieu_chi_moi()

        for q in tim_quan(cau):
            them(tc["quan_huyen"], q)

        for tu, ten in TU_KHOA_DO_DUNG.items():
            if tu in msg:
                them(tc["do_dung"], ten)

        m = re.search(
            r"(\d+(?:[.,]\d+)?)\s*(?:-|đến|tới)\s*(\d+(?:[.,]\d+)?)\s*(?:m2|m²|mét)",
            msg,
        )
        if m:
            tc["dien_tich_min"] = float(m.group(1).replace(",", "."))
            tc["dien_tich_max"] = float(m.group(2).replace(",", "."))
        else:
            m = re.search(
                r"(trên|từ|ít nhất|tối thiểu|dưới|tối đa)?\s*(\d+(?:[.,]\d+)?)\s*(?:m2|m²|mét vuông)",
                msg,
            )
            if m:
                gia_tri = float(m.group(2).replace(",", "."))
                if m.group(1) in ("dưới", "tối đa"):
                    tc["dien_tich_max"] = gia_tri
                else:
                    tc["dien_tich_min"] = gia_tri

        msg_gia = re.sub(r"\d+(?:[.,]\d+)?\s*(?:m2|m²|mét vuông|mét)", " ", msg)
        gia = None

        m = re.search(r"(\d+[.,]\d+)\s*(?:triệu|tr)", msg_gia)
        if m:
            gia = int(round(float(m.group(1).replace(",", ".")) * 1_000_000))
        else:
            m = re.search(r"(\d+)\s*(?:triệu|tr)\s*(\d+)?", msg_gia)
            if m:
                gia = int(m.group(1)) * 1_000_000
                if m.group(2):
                    gia += int(m.group(2)) * (10 ** (6 - len(m.group(2))))
            else:
                m = re.search(r"\b(\d{1,3}(?:[.,]\d{3}){1,2}|\d{6,9})\b", msg_gia)
                if m:
                    gia = int(re.sub(r"[.,]", "", m.group(1)))

        tc["gia_max"] = gia
        return tc

    @staticmethod
    def ap_mo_ho(cau, tc):
        msg = bo_dau(cau)

        for ds_tu, truong, gia_tri, mo_ta in TU_KHOA_MO_HO:
            if tc.get(truong) is not None:
                continue
            if (truong == "dien_tich_min" and tc["dien_tich_max"] is not None
                    and gia_tri > tc["dien_tich_max"]):
                continue
            if (truong == "dien_tich_max" and tc["dien_tich_min"] is not None
                    and gia_tri < tc["dien_tich_min"]):
                continue

            for tu in ds_tu:
                if re.search(r"(?<!\w)" + re.escape(bo_dau(tu)) + r"(?!\w)", msg):
                    tc[truong] = gia_tri
                    tc["suy_luan"].append((mo_ta, truong, gia_tri))
                    break
        return tc

    def xu_ly(self, cau):
        cau = (cau or "").strip()
        if not cau:
            return {
                "status": False,
                "message": "Vui lòng nhập yêu cầu tìm phòng.",
                "criteria": None,
                "nguon": None,
            }

        tc = self.doc_json(self.hoi_gemini(cau))
        nguon = "Gemini"
        if tc is None:
            tc = self.phan_tich(cau)
            nguon = "từ khóa cục bộ"

        if not tc["quan_huyen"]:
            for q in tim_quan(cau):
                them(tc["quan_huyen"], q)

        tc = self.ap_mo_ho(cau, tc)

        dt_min, dt_max = tc["dien_tich_min"], tc["dien_tich_max"]
        if dt_min is not None and dt_max is not None and dt_max < dt_min:
            tc["dien_tich_min"], tc["dien_tich_max"] = dt_max, dt_min
            tc["canh_bao"].append(
                f"Diện tích tối đa ({dt_max:g} m²) nhỏ hơn tối thiểu ({dt_min:g} m²) "
                f"nên đã đổi chỗ hai giá trị"
            )

        return {
            "status": True,
            "message": self.tao_tin(tc),
            "criteria": tc,
            "nguon": nguon,
        }

    @staticmethod
    def tao_tin(tc):
        phan = []
        if tc["quan_huyen"]:
            phan.append("Quận/huyện: " + ", ".join(tc["quan_huyen"]))
        if tc["gia_max"] is not None:
            phan.append(f"Giá tối đa: {tc['gia_max']:,} VNĐ")
        if tc["dien_tich_min"] is not None:
            phan.append(f"Diện tích từ: {tc['dien_tich_min']:g} m²")
        if tc["dien_tich_max"] is not None:
            phan.append(f"Diện tích đến: {tc['dien_tich_max']:g} m²")
        if tc["do_dung"]:
            phan.append("Đồ dùng: " + ", ".join(tc["do_dung"]))

        if not phan:
            return (
                "Mình chưa nhận ra tiêu chí nào trong câu này. "
                "Hãy thử nêu quận/huyện, địa điểm, giá, diện tích hoặc đồ dùng."
            )

        ghi_chu = []
        for mo_ta, truong, gia_tri in tc.get("suy_luan", []):
            if truong == "gia_max":
                ghi_chu.append(f"\"{mo_ta}\" → giá ≤ {gia_tri:,} VNĐ")
            elif truong == "dien_tich_min":
                ghi_chu.append(f"\"{mo_ta}\" → diện tích ≥ {gia_tri:g} m²")
            else:
                ghi_chu.append(f"\"{mo_ta}\" → diện tích ≤ {gia_tri:g} m²")

        tin = "Đã điền bộ lọc - " + " | ".join(phan) + "."
        if ghi_chu:
            tin += " (Suy luận: " + "; ".join(ghi_chu) + ".)"
        if tc.get("canh_bao"):
            tin += " Lưu ý: " + "; ".join(tc["canh_bao"]) + "."
        return tin + " Bấm TÌM KIẾM để xem kết quả."


if __name__ == "__main__":
    bot = ChatbotManager()
    print("Gõ yêu cầu (exit để thoát)")
    while True:
        try:
            cau = input("Bạn: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if cau.lower() in ("exit", "quit"):
            break
        kq = bot.xu_ly(cau)
        print(kq["message"], f"[{kq['nguon']}]")
