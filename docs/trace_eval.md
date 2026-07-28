# 📊 BÁO CÁO GIÁM SÁT & ĐÁNH GIÁ (OBSERVABILITY TRACE LOGS)

**Đề tài**: Trợ Lý Tra Cứu Đơn Hàng & Xử Lý Đổi Trả

---

## 🎯 1. BẢNG CHẤM ĐIỂM AGENTIC FIT (SCORING MATRIX)

| Tiêu chí                       |  Điểm (1-5)  | Lý do đánh giá                                                                                                                                                                                             |
| :------------------------------- | :-------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🧠 **Multi-step Reasoning** | `4/5` | Cần suy luận nhiều bước: xác thực đơn hàng tồn tại (`get_order_details`) → đối chiếu trạng thái giao hàng → áp chính sách đổi trả (`check_return_policy`) trước khi kết luận.                |
| 🛠️ **Tool Interaction**   | `5/5` | LLM không thể tự biết trạng thái một đơn hàng cụ thể — bắt buộc gọi tool tra cứu DB thật (`search_orders_by_phone`, `get_order_details`), và cần tool có **side-effect** để tạo phiếu (`create_return_ticket`). |
| 🔀 **Dynamic Decision**     | `5/5` | Nhánh xử lý phụ thuộc hoàn toàn vào observation: đơn "Giao hàng thành công" vs "Đang vận chuyển" vs "không tồn tại" → 3 phản hồi khác nhau; trong/ngoài hạn 7 ngày cũng rẽ nhánh khác nhau.                     |
| ⏳ **Long Horizon**         | `3/5` | Luồng đầy đủ gồm tối đa 3 lời gọi tool (tra cứu đơn → kiểm tra chính sách → tạo phiếu), có thể trải qua 2 lượt hội thoại nếu cần xác nhận trước khi tạo phiếu.                                              |
| **TỔNG ĐIỂM FIT**       | **17/20** | **KẾT LUẬN: RẤT NÊN DÙNG REACT AGENT** — câu trả lời đúng phụ thuộc vào dữ liệu đơn hàng thật (DB) mà Chatbot thuần LLM không thể biết hay bịa ra một cách an toàn.                                       |

---

## 🔍 2. SO SÁNH PHẢN HỒI: CHATBOT BASELINE vs REACT AGENT

> Các giá trị `Observation` bên dưới được suy trực tiếp từ logic thật trong `src/tools.py` (hàm thuần, dữ liệu mock cố định `MOCK_ORDERS_DB`) nên chính xác tuyệt đối. Phần `Thought`/`Final Answer` do LLM sinh ra tại runtime nên chỉ mang tính minh họa cho định dạng ReAct mong đợi.

### Test Case A — Đổi trả hợp lệ (đơn còn trong hạn)

**Câu hỏi**: *"Đơn hàng DH1001 của tôi bị chật size, tôi muốn đổi trả có được không?"*

**🤖 Chatbot Baseline**:
* **Phản hồi**: *"Tôi không có quyền truy cập hệ thống đơn hàng nên không thể xác nhận tình trạng đơn DH1001. Bạn vui lòng liên hệ CSKH để được hỗ trợ."*
* **Nhận xét**: An toàn (không bịa trạng thái đơn) nhưng không giải quyết được nhu cầu.

**🧠 ReAct Agent — Lượt 1**:
* **Thought 1**: Cần xác minh đơn hàng DH1001 trước khi đánh giá đổi trả.
* **Action 1**: `get_order_details["DH1001"]`
* **Observation 1**: `Thông tin đơn hàng [DH1001]: Ngày đặt hàng: 2026-07-20, Trạng thái: Giao hàng thành công, Danh mục: Thời trang, Sản phẩm: Áo sơ mi Nam Size L (x1), Tổng tiền: 350,000 VNĐ.`
* **Thought 2**: Đơn đã giao thành công, cần kiểm tra chính sách đổi trả với lý do "Mặc không vừa size".
* **Action 2**: `check_return_policy["DH1001", "Mặc không vừa size"]`
* **Observation 2**: `ĐỦ ĐIỀU KIỆN ĐỔI TRẢ: Trong thời hạn 7 ngày kể từ khi giao thành công. Gợi ý Action tiếp theo: gọi tool 'create_return_ticket'.`
* **Final Answer**: *"Đơn DH1001 (Áo sơ mi Nam Size L) đủ điều kiện đổi trả. Bạn có muốn tôi tạo phiếu đổi trả ngay bây giờ không?"*

**🧠 ReAct Agent — Lượt 2** (sau khi khách xác nhận "Có"):
* **Thought 1**: Khách đã đồng ý, tiến hành tạo phiếu đổi trả cho DH1001.
* **Action 1**: `create_return_ticket["DH1001", "Mặc không vừa size", "Đổi size/mẫu"]`
* **Observation 1**: `TẠO PHIẾU ĐỔI TRẢ THÀNH CÔNG! Mã phiếu: RET_DH1001_2026. Đóng gói sản phẩm và gửi về kho theo mã phiếu, shipper tới lấy trong 24h-48h.`
* **Final Answer**: *"Đã tạo phiếu đổi trả RET_DH1001_2026 cho đơn DH1001. Vui lòng đóng gói sản phẩm, shipper sẽ tới lấy trong 24-48h."*

> ⚠️ **Ghi chú Guardrail**: `MAX_ITERATIONS = 3` trong `prompts.py`. Luồng đầy đủ 1 lượt (tra cứu + kiểm tra + tạo phiếu = 3 Action) cộng thêm 1 Final Answer sẽ chạm/​vượt giới hạn 3 vòng lặp. Vì vậy tách thành 2 lượt hội thoại (hỏi xác nhận trước khi tạo phiếu) là cách thiết kế phù hợp với guardrail hiện tại, thay vì để Agent tự động làm hết trong 1 lượt.

### Test Case B — Từ chối đổi trả (quá hạn / sai trạng thái)

**Câu hỏi**: *"Đơn DH1002 của tôi (tai nghe) tôi muốn trả lại vì đổi ý."*

* **Thought 1**: Cần xác minh đơn hàng DH1002.
* **Action 1**: `get_order_details["DH1002"]`
* **Observation 1**: `... Ngày đặt hàng: 2026-06-01, Trạng thái: Giao hàng thành công, Sản phẩm: Tai nghe Bluetooth X1 (x1) ...`
* **Thought 2**: Đơn đã giao thành công, kiểm tra chính sách đổi trả.
* **Action 2**: `check_return_policy["DH1002", "Đổi ý"]`
* **Observation 2**: `TỪ CHỐI ĐỔI TRẢ: Đơn hàng 'DH1002' được mua ngày 2026-06-01 (Đã quá thời hạn 7 ngày đổi trả theo quy định).`
* **Final Answer**: *"Rất tiếc, đơn DH1002 đã quá thời hạn 7 ngày đổi trả nên không thể xử lý theo lý do đổi ý. Bạn có thể liên hệ CSKH để được hỗ trợ thêm."*

> ⚠️ **Ghi chú quan sát**: `check_return_policy` chỉ hard-code từ chối đúng mã `DH1002`, không thật sự tính số ngày từ `order_date`. Với đơn `DH1001` (đặt 2026-07-20, cũng đã 8 ngày tính tới hôm nay) hàm vẫn trả về "ĐỦ ĐIỀU KIỆN" — sai lệch so với comment thiết kế ban đầu ("quá hạn 7 ngày"). Cần lưu ý khi đọc log thật: nếu Agent chấp nhận đổi trả cho các đơn đã đặt hơn 7 ngày (trừ DH1002), đó là do giới hạn của mock data, không phải lỗi suy luận của Agent.

### Test Case C — Bẫy Guardrail (mã đơn không tồn tại)

**Câu hỏi**: *"Tra cứu đơn hàng DH9999 giúp tôi."*

* **Thought 1**: Cần tra cứu đơn hàng DH9999.
* **Action 1**: `get_order_details["DH9999"]`
* **Observation 1**: `LỖI: Không tìm thấy mã đơn hàng 'DH9999' trong hệ thống. Vui lòng kiểm tra lại mã đơn.`
* **Thought 2**: Không có dữ liệu, không được suy đoán hay bịa trạng thái đơn hàng.
* **Final Answer**: *"Tôi không tìm thấy đơn hàng DH9999 trong hệ thống. Bạn kiểm tra lại mã đơn giúp tôi nhé."*
* Nếu Agent cố gọi lại tool nhiều lần với mã khác nhau mà vẫn lỗi → **GUARDRAIL TRIGGERED** sau `MAX_ITERATIONS` bước, trả lời lịch sự thay vì lặp vô hạn.