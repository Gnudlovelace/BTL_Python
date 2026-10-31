"""
Chatbot trích xuất bộ lọc tìm phòng trọ từ câu nói tự nhiên.

Đầu vào : "trọ gần Bưu chính viễn thông, dưới 3 triệu, có điều hòa"
Đầu ra  : {
    "quan_huyen": ["Hà Đông", "Thanh Xuân", ...],
    "gia_max": 3000000,
    "dien_tich_min": None,
    "dien_tich_max": None,
    "do_dung": ["Điều hòa"],
}

- Ưu tiên gọi Gemini (cần `pip install google-genai` và GEMINI_API_KEY).
- Nếu không có thư viện / API key / API lỗi -> tự động dùng bộ phân tích
  từ khóa cục bộ (fallback), nên chatbot luôn hoạt động.
"""


import json
import re
import time

from .cau_hinh import (
    GEMINI_API_KEY, GEMINI_MODEL, DANH_SACH_QUAN_HUYEN, DANH_SACH_DO_DUNG,
    NGUONG_RE, NGUONG_RONG, NGUONG_NHO, TU_KHOA_MO_HO, TU_KHOA_DO_DUNG,
)
from .xu_ly_van_ban import (
    _chuan_hoa_ten, _them_khong_trung, _bo_dau, tim_quan_huyen_trong_cau,
)


def _tieu_chi_rong():
    return {
        "quan_huyen": [],
        "gia_max": None,
        "dien_tich_min": None,
        "dien_tich_max": None,
        "do_dung": [],
        "suy_luan": [],   # ghi chú: từ mô tả mơ hồ đã được quy đổi thế nào
        "canh_bao": [],   # cảnh báo: ví dụ diện tích min/max bị mâu thuẫn
    }


class ChatbotManager:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model or GEMINI_MODEL
        self.client = None

        if self.api_key:
            try:
                from google import genai

                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:  # thiếu thư viện hoặc key sai
                print(f"[Chatbot] Không khởi tạo được Gemini: {e}")
                self.client = None

    # Gemini
    def _goi_gemini(self, cau_hoi):
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

Yêu cầu người dùng: "{cau_hoi}"

CHỈ TRẢ VỀ MỘT ĐỐI TƯỢNG JSON HỢP LỆ, KHÔNG GIẢI THÍCH, KHÔNG DÙNG MARKDOWN.
"""
        for lan in range(1, 3):
            try:
                response = self.client.models.generate_content(
                    model=self.model, contents=prompt
                )
                return response.text
            except Exception as e:
                print(f"[Chatbot] Gemini lần {lan} lỗi: {e}")
                if lan < 2:
                    time.sleep(1)
        return None

    def _parse_json(self, raw):
        if not raw:
            return None
        try:
            sach = re.sub(r"```(?:json)?", "", raw, flags=re.IGNORECASE).strip()
            # lấy đối tượng JSON đầu tiên nếu model nói thừa
            m = re.search(r"\{.*\}", sach, flags=re.DOTALL)
            data = json.loads(m.group(0) if m else sach)
        except Exception:
            return None

        tieu_chi = _tieu_chi_rong()

        for q in data.get("quan_huyen") or []:
            _them_khong_trung(
                tieu_chi["quan_huyen"], _chuan_hoa_ten(q, DANH_SACH_QUAN_HUYEN)
            )
        for d in data.get("do_dung") or []:
            _them_khong_trung(
                tieu_chi["do_dung"], _chuan_hoa_ten(d, DANH_SACH_DO_DUNG)
            )

        def so(giá_tri, kieu):
            try:
                return kieu(giá_tri) if giá_tri is not None else None
            except (TypeError, ValueError):
                return None

        tieu_chi["gia_max"] = so(data.get("gia_max"), int)
        tieu_chi["dien_tich_min"] = so(data.get("dien_tich_min"), float)
        tieu_chi["dien_tich_max"] = so(data.get("dien_tich_max"), float)
        return tieu_chi

    # Fallback cục bộ
    def _phan_tich_tu_khoa(self, cau_hoi):
        msg = cau_hoi.casefold()
        tieu_chi = _tieu_chi_rong()

        # 1 + 2. Quận / huyện nêu trực tiếp và địa danh -> quận / huyện lân cận
        for q in tim_quan_huyen_trong_cau(cau_hoi):
            _them_khong_trung(tieu_chi["quan_huyen"], q)

        # 3. Đồ dùng
        for tu_khoa, ten in TU_KHOA_DO_DUNG.items():
            if tu_khoa in msg:
                _them_khong_trung(tieu_chi["do_dung"], ten)

        # 4. Diện tích: "20m2", "từ 20 đến 30 m2", "trên 25m2"
        m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:-|đến|tới)\s*(\d+(?:[.,]\d+)?)\s*(?:m2|m²|mét)", msg)
        if m:
            tieu_chi["dien_tich_min"] = float(m.group(1).replace(",", "."))
            tieu_chi["dien_tich_max"] = float(m.group(2).replace(",", "."))
        else:
            m = re.search(r"(trên|từ|ít nhất|tối thiểu|dưới|tối đa)?\s*(\d+(?:[.,]\d+)?)\s*(?:m2|m²|mét vuông)", msg)
            if m:
                gia_tri = float(m.group(2).replace(",", "."))
                if m.group(1) in ("dưới", "tối đa"):
                    tieu_chi["dien_tich_max"] = gia_tri
                else:
                    tieu_chi["dien_tich_min"] = gia_tri

        # 5. Giá: "3 triệu", "3.5tr", "3tr5", "4000000"
        gia_msg = re.sub(r"\d+(?:[.,]\d+)?\s*(?:m2|m²|mét vuông|mét)", " ", msg)
        gia = None
        # Số thập phân trước ("3.5 triệu"), rồi "3tr5" / "3 triệu", rồi số đầy đủ
        m = re.search(r"(\d+[.,]\d+)\s*(?:triệu|tr)", gia_msg)
        if m:
            gia = int(round(float(m.group(1).replace(",", ".")) * 1_000_000))
        else:
            m = re.search(r"(\d+)\s*(?:triệu|tr)\s*(\d+)?", gia_msg)
            if m:
                gia = int(m.group(1)) * 1_000_000
                if m.group(2):  # "3tr5" -> 3.5 triệu
                    gia += int(m.group(2)) * (10 ** (6 - len(m.group(2))))
            else:
                m = re.search(r"\b(\d{1,3}(?:[.,]\d{3}){1,2}|\d{6,9})\b", gia_msg)
                if m:
                    gia = int(re.sub(r"[.,]", "", m.group(1)))
        tieu_chi["gia_max"] = gia
        return tieu_chi

    # Từ mô tả mơ hồ ("rẻ", "rộng"...) -> giá trị cụ thể
    @staticmethod
    def _ap_dung_tu_khoa_mo_ho(cau_hoi, tieu_chi):
        """Điền các trường còn trống dựa trên từ mô tả mơ hồ.
        Không ghi đè giá trị mà người dùng đã nêu cụ thể (hoặc Gemini đã điền)."""
        msg = _bo_dau(cau_hoi)   # so khớp không dấu: "tro re" cũng hiểu là "trọ rẻ"
        for tu_khoa, truong, gia_tri, mo_ta in TU_KHOA_MO_HO:
            if tieu_chi.get(truong) is not None:
                continue
            # Không áp dụng nếu làm diện tích min > max (mâu thuẫn với số đã nêu)
            if (truong == "dien_tich_min" and tieu_chi["dien_tich_max"] is not None
                    and gia_tri > tieu_chi["dien_tich_max"]):
                continue
            if (truong == "dien_tich_max" and tieu_chi["dien_tich_min"] is not None
                    and gia_tri < tieu_chi["dien_tich_min"]):
                continue
            for tk in tu_khoa:
                if re.search(r"(?<!\w)" + re.escape(_bo_dau(tk)) + r"(?!\w)", msg):
                    tieu_chi[truong] = gia_tri
                    tieu_chi["suy_luan"].append((mo_ta, truong, gia_tri))
                    break
        return tieu_chi

    # Hàm chính
    def xu_ly_cau_hoi(self, cau_hoi):
        """Trả về dict: {status, message, criteria, nguon}."""
        cau_hoi = (cau_hoi or "").strip()
        if not cau_hoi:
            return {
                "status": False,
                "message": "Vui lòng nhập yêu cầu tìm phòng.",
                "criteria": None,
                "nguon": None,
            }

        tieu_chi = self._parse_json(self._goi_gemini(cau_hoi))
        nguon = "Gemini"
        if tieu_chi is None:
            tieu_chi = self._phan_tich_tu_khoa(cau_hoi)
            nguon = "từ khóa cục bộ"

        # Gemini không ra quận/huyện -> thử tra từ điển địa danh cục bộ
        if not tieu_chi["quan_huyen"]:
            for q in tim_quan_huyen_trong_cau(cau_hoi):
                _them_khong_trung(tieu_chi["quan_huyen"], q)

        # Bổ sung các yếu tố mơ hồ mà phần trên chưa bắt được
        tieu_chi = self._ap_dung_tu_khoa_mo_ho(cau_hoi, tieu_chi)

        # Diện tích tối đa không được nhỏ hơn tối thiểu
        dt_min, dt_max = tieu_chi["dien_tich_min"], tieu_chi["dien_tich_max"]
        if dt_min is not None and dt_max is not None and dt_max < dt_min:
            tieu_chi["dien_tich_min"], tieu_chi["dien_tich_max"] = dt_max, dt_min
            tieu_chi["canh_bao"].append(
                f"Diện tích tối đa ({dt_max:g} m²) nhỏ hơn tối thiểu ({dt_min:g} m²) "
                f"nên đã đổi chỗ hai giá trị"
            )

        return {
            "status": True,
            "message": self.tao_thong_bao(tieu_chi),
            "criteria": tieu_chi,
            "nguon": nguon,
        }

    @staticmethod
    def tao_thong_bao(tc):
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

        ghi_chu = []
        for mo_ta, truong, gia_tri in tc.get("suy_luan", []):
            if truong == "gia_max":
                ghi_chu.append(f"\"{mo_ta}\" → giá ≤ {gia_tri:,} VNĐ")
            elif truong == "dien_tich_min":
                ghi_chu.append(f"\"{mo_ta}\" → diện tích ≥ {gia_tri:g} m²")
            else:
                ghi_chu.append(f"\"{mo_ta}\" → diện tích ≤ {gia_tri:g} m²")

        if not phan:
            return (
                "Mình chưa nhận ra tiêu chí nào trong câu này. "
                "Hãy thử nêu quận/huyện, địa điểm, giá, diện tích hoặc đồ dùng."
            )
        thong_bao = "Đã điền bộ lọc - " + " | ".join(phan) + "."
        if ghi_chu:
            thong_bao += " (Suy luận: " + "; ".join(ghi_chu) + ".)"
        if tc.get("canh_bao"):
            thong_bao += " Lưu ý: " + "; ".join(tc["canh_bao"]) + "."
        return thong_bao + " Bấm TÌM KIẾM để xem kết quả."


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
        kq = bot.xu_ly_cau_hoi(cau)
        print(kq["message"], f"[{kq['nguon']}]")
