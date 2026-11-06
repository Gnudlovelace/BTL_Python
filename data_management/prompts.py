def tao_prompt(mo_dau, vi_du, quy_tac_them=""):
    return mo_dau + """

{du_lieu}

Hãy trả về MỘT JSON ARRAY hợp lệ, mỗi bài đúng một object với các key:

{
    "url": "Giữ nguyên URL",
    "gia_dien": 4000,
    "gia_nuoc": 100000,
    "gia_dich_vu": null,
    "do_dung_hien_co": """ + vi_du + """
}

Quy tắc:
1. Giữ nguyên URL, không trộn thông tin giữa các bài.
2. gia_dien, gia_nuoc, gia_dich_vu: số nguyên (đồng), chỉ lấy số; không có thì null.
3. Không có đồ dùng thì trả về [].
4. Phải trả về đủ một object cho mỗi bài.
5. Chỉ trả về JSON ARRAY, không có markdown.
""" + quy_tac_them


PROMPT_GULAND = tao_prompt(
    "Bạn đang xử lý dữ liệu của nhiều bài đăng thuê phòng trọ.\n\n"
    "Dưới đây là danh sách các bài đăng:",
    '["điều hòa", "nóng lạnh", "giường"]',
)

PROMPT_PHONGTRO123 = tao_prompt(
    "Bạn đang xử lý mô tả của nhiều bài đăng cho thuê phòng trọ. Mô tả rất lộn xộn:\n"
    "có số điện thoại, tên trường đại học lân cận, địa chỉ, giờ giấc, khuyến mãi,\n"
    "ký tự trang trí (=====, emoji)... TẤT CẢ những thông tin đó phải BỊ BỎ QUA.\n\n"
    "Dưới đây là danh sách các bài đăng (thong_tin_them là phần mô tả):",
    '["tủ bếp", "tủ quần áo", "điều hòa", "nóng lạnh", "giường", "đệm"]',
    """6. do_dung_hien_co CHỈ gồm tên đồ nội thất / thiết bị có sẵn trong phòng
   (ví dụ: giường, đệm, tủ quần áo, tủ bếp, điều hòa, nóng lạnh, tủ lạnh,
   máy giặt, quạt trần, bàn ghế, ban công, wc riêng, khóa vân tay...).
7. Viết tắt phải chuẩn hóa thành tên đầy đủ (ĐH -> điều hòa, BNL -> bình nóng lạnh, ...).
   Mỗi món là một phần tử ngắn gọn, viết thường, không trùng lặp.
8. KHÔNG đưa vào danh sách: số điện thoại, địa chỉ, tên trường, giờ giấc, camera/an ninh,
   giá, câu quảng cáo hay bất kỳ thông tin nào không phải đồ dùng.
""",
)
