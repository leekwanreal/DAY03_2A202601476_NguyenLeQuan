# 🌐 HƯỚNG DẪN KHỞI CHẠY VÀ DEPLOY WEB UI DÀNH CHO CSKH AI AGENT

Thư mục `web_ui/` chứa giao diện Web UI tương tác hiện đại dành cho hệ thống CSKH AI Agent (Tra cứu đơn hàng & Đổi trả sản phẩm).

---

## 🚀 1. Cách chạy Web UI trên máy cục bộ (Localhost)

Chỉ cần chạy 1 lệnh Python (Không cần cài thêm bất kỳ thư viện ngoài nào vì đã dùng thư viện chuẩn `http.server` của Python):

```bash
python web_ui/server.py
```

Sau đó mở trình duyệt web và truy cập đường dẫn:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🌟 2. Tính năng nổi bật của Web UI

- **Giao diện Chat Dark Mode Glassmorphism**: Thiết kế sang trọng, hiện đại với font Inter & Outfit từ Google Fonts.
- **Trình diễn ReAct Execution Trace**: Hiển thị trực quan từng bước `Thought` ➔ `Action` ➔ `Observation` ➔ `Final Answer`.
- **Nút bấm Test Cases mẫu**: Tự động chèn câu hỏi kiểm thử từ `config/test_cases.json`.
- **Cơ sở dữ liệu mẫu (Mock DB Dashboard)**: Xem nhanh trạng thái các đơn hàng `DH1001`, `DH1002`, `DH1003` trực tiếp trên Sidebar.
- **Chuyển đổi chế độ Agent linh hoạt**:
  - `ReAct Agent (Tool & Trace)`
  - `Baseline Chatbot (Không dùng Tool)`
  - `Autonomous Goal Agent`

---

## 🌐 3. Gợi ý đưa Web UI lên Host / Cloud (Web Deployment)

Nếu bạn muốn deploy web này cho giảng viên hoặc đội nhóm truy cập từ xa:
1. **Nodemon / Python Web Hosting (Render / Railway / PythonAnywhere)**:
   - Upload toàn bộ dự án lên GitHub.
   - Tạo Service trên [Render.com](https://render.com) hoặc [Railway.app](https://railway.app).
   - Đặt **Start Command**: `python web_ui/server.py`.
2. **Ngrok (Chia sẻ nhanh qua Internet trong vài giây)**:
   - Chạy `python web_ui/server.py` ở cổng 8000.
   - Gõ lệnh Ngrok: `ngrok http 8000` ➔ Nhận ngay đường link HTTPS công khai để gửi cho người khác test!