"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Chủ đề: Trợ Lý Tra Cứu Đơn Hàng & Xử Lý Đổi Trả
"""

import json

# Mock Data mô phỏng Cơ sở dữ liệu Đơn hàng
MOCK_ORDERS_DB = {
    "DH1001": {
        "order_id": "DH1001",
        "customer_phone": "0901234567",
        "order_date": "2026-07-20",  # Mua cách đây 8 ngày
        "status": "Giao hàng thành công",
        "items": [
            {"item_id": "SP01", "name": "Áo sơ mi Nam Size L", "price": 350000, "quantity": 1}
        ],
        "total_amount": 350000,
        "category": "Thời trang",
    },
    "DH1002": {
        "order_id": "DH1002",
        "customer_phone": "0901234567",
        "order_date": "2026-06-01",  # Mua quá 30 ngày
        "status": "Giao hàng thành công",
        "items": [
            {"item_id": "SP02", "name": "Tai nghe Bluetooth X1", "price": 850000, "quantity": 1}
        ],
        "total_amount": 850000,
        "category": "Điện tử",
    },
    "DH1003": {
        "order_id": "DH1003",
        "customer_phone": "0988888888",
        "order_date": "2026-07-26",
        "status": "Đang vận chuyển",
        "items": [
            {"item_id": "SP03", "name": "Giày Sneaker Size 42", "price": 1200000, "quantity": 1}
        ],
        "total_amount": 1200000,
        "category": "Thời trang",
    },
    "DH1004": {
        "order_id": "DH1004",
        "customer_phone": "0912345678",
        "order_date": "2026-07-28",
        "status": "Chờ xác nhận",
        "items": [
            {"item_id": "SP04", "name": "Bàn phím cơ K8", "price": 1500000, "quantity": 1},
            {"item_id": "SP05", "name": "Chuột không dây M3", "price": 300000, "quantity": 1}
        ],
        "total_amount": 1800000,
        "category": "Điện tử",
    },
    "DH1005": {
        "order_id": "DH1005",
        "customer_phone": "0933333333",
        "order_date": "2026-07-10",
        "status": "Giao hàng thành công",
        "items": [
            {"item_id": "SP06", "name": "Kem chống nắng SPF 50", "price": 450000, "quantity": 2}
        ],
        "total_amount": 900000,
        "category": "Mỹ phẩm",
    },
    "DH1006": {
        "order_id": "DH1006",
        "customer_phone": "0901234567",  # Khách hàng quen
        "order_date": "2026-07-25",
        "status": "Đã hủy",
        "items": [
            {"item_id": "SP07", "name": "Nồi chiên không dầu 5L", "price": 1800000, "quantity": 1}
        ],
        "total_amount": 1800000,
        "category": "Gia dụng",
    },
    "DH1007": {
        "order_id": "DH1007",
        "customer_phone": "0977777777",
        "order_date": "2026-07-27",
        "status": "Đang đóng gói",
        "items": [
            {"item_id": "SP08", "name": "Balo laptop chống nước", "price": 650000, "quantity": 1}
        ],
        "total_amount": 650000,
        "category": "Thời trang",
    },
    "DH1008": {
        "order_id": "DH1008",
        "customer_phone": "0966666666",
        "order_date": "2026-05-15",
        "status": "Giao hàng thành công",
        "items": [
            {"item_id": "SP09", "name": "Thảm tập Yoga", "price": 250000, "quantity": 1}
        ],
        "total_amount": 250000,
        "category": "Thể thao",
    },
    "DH1009": {
        "order_id": "DH1009",
        "customer_phone": "0944444444",
        "order_date": "2026-07-22",
        "status": "Giao hàng thành công",
        "items": [
            {"item_id": "SP10", "name": "Màn hình 24 inch", "price": 3200000, "quantity": 1}
        ],
        "total_amount": 3200000,
        "category": "Điện tử",
    },
    "DH1010": {
        "order_id": "DH1010",
        "customer_phone": "0922222222",
        "order_date": "2026-07-27",
        "status": "Đang vận chuyển",
        "items": [
            {"item_id": "SP11", "name": "Sữa rửa mặt", "price": 150000, "quantity": 3}
        ],
        "total_amount": 450000,
        "category": "Mỹ phẩm",
    },
    "DH1011": {
        "order_id": "DH1011",
        "customer_phone": "0955555555",
        "order_date": "2026-07-28",
        "status": "Chờ xác nhận",
        "items": [
            {"item_id": "SP12", "name": "Áo khoác gió", "price": 550000, "quantity": 1}
        ],
        "total_amount": 550000,
        "category": "Thời trang",
    },
    "DH1012": {
        "order_id": "DH1012",
        "customer_phone": "0911111111",
        "order_date": "2026-07-01",
        "status": "Giao hàng thành công",
        "items": [
            {"item_id": "SP13", "name": "Loa Bluetooth Mini", "price": 400000, "quantity": 2}
        ],
        "total_amount": 800000,
        "category": "Điện tử",
    },
    "DH1013": {
        "order_id": "DH1013",
        "customer_phone": "0988888888",
        "order_date": "2026-07-26",
        "status": "Đã hủy",
        "items": [
            {"item_id": "SP14", "name": "Bộ tạ tay 10kg", "price": 750000, "quantity": 1}
        ],
        "total_amount": 750000,
        "category": "Thể thao",
    },
    "DH1014": {
        "order_id": "DH1014",
        "customer_phone": "0900000000",
        "order_date": "2026-07-18",
        "status": "Giao hàng thành công",
        "items": [
            {"item_id": "SP15", "name": "Quạt lửng", "price": 500000, "quantity": 1},
            {"item_id": "SP16", "name": "Ổ cắm điện 6 lỗ", "price": 120000, "quantity": 2}
        ],
        "total_amount": 740000,
        "category": "Gia dụng",
    },
    "DH1015": {
        "order_id": "DH1015",
        "customer_phone": "0934567890",
        "order_date": "2026-07-28",
        "status": "Đang vận chuyển",
        "items": [
            {"item_id": "SP17", "name": "Đồng hồ thông minh", "price": 2500000, "quantity": 1}
        ],
        "total_amount": 2500000,
        "category": "Điện tử",
    },
    "DH1016": {
        "order_id": "DH1016",
        "customer_phone": "0999999999",
        "order_date": "2026-06-20",
        "status": "Giao hàng thành công",
        "items": [
            {"item_id": "SP18", "name": "Quần Jeans Nam", "price": 450000, "quantity": 2}
        ],
        "total_amount": 900000,
        "category": "Thời trang",
    },
    "DH1017": {
        "order_id": "DH1017",
        "customer_phone": "0901234567",
        "order_date": "2026-07-21",
        "status": "Giao hàng thành công",
        "items": [
            {"item_id": "SP19", "name": "Dầu gội thảo dược", "price": 250000, "quantity": 1}
        ],
        "total_amount": 250000,
        "category": "Mỹ phẩm",
    },
    "DH1018": {
        "order_id": "DH1018",
        "customer_phone": "0971234567",
        "order_date": "2026-07-28",
        "status": "Đang đóng gói",
        "items": [
            {"item_id": "SP20", "name": "Máy xay sinh tố", "price": 850000, "quantity": 1}
        ],
        "total_amount": 850000,
        "category": "Gia dụng",
    },
    "DH1019": {
        "order_id": "DH1019",
        "customer_phone": "0961234567",
        "order_date": "2026-07-15",
        "status": "Giao hàng thành công",
        "items": [
            {"item_id": "SP21", "name": "Vợt cầu lông", "price": 1100000, "quantity": 2}
        ],
        "total_amount": 2200000,
        "category": "Thể thao",
    },
    "DH1020": {
        "order_id": "DH1020",
        "customer_phone": "0951234567",
        "order_date": "2026-07-25",
        "status": "Giao hàng thành công",
        "items": [
            {"item_id": "SP22", "name": "Pin sạc dự phòng 10000mAh", "price": 350000, "quantity": 1},
            {"item_id": "SP23", "name": "Cáp sạc Type-C", "price": 90000, "quantity": 1}
        ],
        "total_amount": 440000,
        "category": "Điện tử",
    }
}

def search_orders_by_phone(phone_number: str) -> str:
    """
    Tra cứu danh sách các mã đơn hàng gắn liền với số điện thoại của khách hàng.
    
    Args:
        phone_number (str): Số điện thoại của khách hàng (Ví dụ: '0901234567')
        
    Returns:
        str: Chuỗi định dạng danh sách mã đơn hàng hoặc thông báo lỗi nếu không tìm thấy.
    """
    phone_clean = phone_number.strip().replace(" ", "")
    found_orders = [
        f"- Mã đơn: {oid} (Ngày mua: {info['order_date']}, Trạng thái: {info['status']})"
        for oid, info in MOCK_ORDERS_DB.items()
        if info["customer_phone"] == phone_clean
    ]
    
    if not found_orders:
        return f"LỖI: Không tìm thấy đơn hàng nào gắn với số điện thoại '{phone_number}'."
        
    return f"Tìm thấy {len(found_orders)} đơn hàng cho SĐT {phone_number}:\n" + "\n".join(found_orders)


def get_order_details(order_id: str) -> str:
    """
    Tra cứu thông tin chi tiết của một đơn hàng cụ thể theo mã đơn hàng.
    
    Args:
        order_id (str): Mã đơn hàng (Ví dụ: 'DH1001', 'DH1002')
        
    Returns:
        str: Chi tiết đơn hàng dạng chuỗi văn bản rõ ràng.
    """
    order_key = order_id.strip().upper()
    if order_key not in MOCK_ORDERS_DB:
        return f"LỖI: Không tìm thấy mã đơn hàng '{order_id}' trong hệ thống. Vui lòng kiểm tra lại mã đơn."
    
    order = MOCK_ORDERS_DB[order_key]
    items_str = ", ".join([f"{item['name']} (x{item['quantity']})" for item in order["items"]])
    
    return (
        f"Thông tin đơn hàng [{order['order_id']}]:\n"
        f"- Ngày đặt hàng: {order['order_date']}\n"
        f"- Trạng thái: {order['status']}\n"
        f"- Danh mục: {order['category']}\n"
        f"- Sản phẩm: {items_str}\n"
        f"- Tổng tiền: {order['total_amount']:,} VNĐ\n"
        f"- Số điện thoại khách: {order['customer_phone']}"
    )


def check_return_policy(order_id: str, reason: str) -> str:
    """
    Kiểm tra điều kiện đổi trả của đơn hàng dựa trên chính sách (Thời hạn 7 ngày kể từ khi nhận hàng, ngành hàng, lý do).
    
    Args:
        order_id (str): Mã đơn hàng cần kiểm tra (Ví dụ: 'DH1001')
        reason (str): Lý do đổi trả (Ví dụ: 'Mặc không vừa size', 'Hàng bị lỗi', 'Đổi ý')
        
    Returns:
        str: Kết quả đánh giá điều kiện đổi trả và hướng xử lý tiếp theo.
    """
    order_key = order_id.strip().upper()
    if order_key not in MOCK_ORDERS_DB:
        return f"LỖI: Không thể kiểm tra chính sách vì không tìm thấy mã đơn '{order_id}'."
        
    order = MOCK_ORDERS_DB[order_key]
    
    # Kiểm tra trạng thái đơn
    if order["status"] != "Giao hàng thành công":
        return f"TỪ CHỐI ĐỔI TRẢ: Đơn hàng '{order_id}' đang ở trạng thái '{order['status']}'. Chỉ áp dụng đổi trả cho đơn đã giao thành công."
    
    # Giả lập logic kiểm tra số ngày
    if order_key == "DH1002":
        return f"TỪ CHỐI ĐỔI TRẢ: Đơn hàng '{order_id}' được mua ngày {order['order_date']} (Đã quá thời hạn 7 ngày đổi trả theo quy định)."
        
    # Đủ điều kiện
    return (
        f"ĐỦ ĐIỀU KIỆN ĐỔI TRẢ:\n"
        f"- Đơn hàng: {order_id}\n"
        f"- Lý do ghi nhận: '{reason}'\n"
        f"- Điều kiện: Trong thời hạn 7 ngày kể từ khi giao thành công.\n"
        f"- Gợi ý Action tiếp theo: Bạn có thể thực hiện gọi tool 'create_return_ticket' để tạo yêu cầu."
    )


def create_return_ticket(order_id: str, reason: str, return_type: str = "Đổi size/mẫu") -> str:
    """
    Tạo yêu cầu/phiếu đổi trả hàng chính thức vào hệ thống cho đơn hàng.
    
    Args:
        order_id (str): Mã đơn hàng cần tạo đổi trả (Ví dụ: 'DH1001')
        reason (str): Lý do chi tiết đổi trả
        return_type (str): Loại yêu cầu ('Đổi size/mẫu' hoặc 'Hoàn tiền')
        
    Returns:
        str: Mã phiếu đổi trả và hướng dẫn gửi trả hàng cho khách.
    """
    order_key = order_id.strip().upper()
    if order_key not in MOCK_ORDERS_DB:
        return f"LỖI: Tạo phiếu thất bại. Không tìm thấy mã đơn hàng '{order_id}'."
        
    ticket_id = f"RET_{order_key}_2026"
    return (
        f"TẠO PHIẾU ĐỔI TRẢ THÀNH CÔNG!\n"
        f"- Mã phiếu đổi trả: {ticket_id}\n"
        f"- Đơn hàng: {order_id}\n"
        f"- Hình thức: {return_type}\n"
        f"- Lý do: {reason}\n"
        f"- Hướng dẫn khách hàng: Đóng gói sản phẩm và gửi về kho theo mã phiếu {ticket_id}. Shiper sẽ tới lấy trong 24h-48h."
    )


# ---------------------------------------------------------
# DANH SÁCH TẤT CẢ CÁC TOOL ĐƯỢC ĐĂNG KÝ CHO REACT AGENT
# ---------------------------------------------------------
AVAILABLE_TOOLS = {
    "search_orders_by_phone": search_orders_by_phone,
    "get_order_details": get_order_details,
    "check_return_policy": check_return_policy,
    "create_return_ticket": create_return_ticket,
}


# Chạy thử tool
if __name__ == "__main__":
    print("--- TEST TOOL 1: Tra cứu theo SĐT ---")
    print(search_orders_by_phone("0988888888"))
    
    print("\n--- TEST TOOL 2: Chi tiết đơn hàng ---")
    print(get_order_details("DH1001"))
    
    print("\n--- TEST TOOL 3: Test lỗi nhập sai mã đơn ---")
    print(get_order_details("DH100112313")) # Phải ra chuỗi LỖI, không crash app!

    print("\n--- TEST TOOL 4: Tạo phiếu đổi trả hàng ---")
    print(create_return_ticket(order_id="DH1001", reason="Không đẹp"))