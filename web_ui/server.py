"""
🌐 WEB SERVER BACKEND FOR CSKH ORDER TRACKING & RETURN AI AGENT
Sử dụng thư viện chuẩn http.server của Python (Zero extra dependencies).
Chạy lệnh: python web_ui/server.py
"""

import http.server
import socketserver
import json
import os
import sys
import urllib.parse

# Thêm thư mục gốc dự án và thư mục src/ vào sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from tools import MOCK_ORDERS_DB, search_orders_by_phone, get_order_details, check_return_policy, create_return_ticket, AVAILABLE_TOOLS
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS, GUARDRAIL_FALLBACK_RESPONSES
from providers import get_llm_provider

PORT = 8000
WEB_DIR = os.path.dirname(os.path.abspath(__file__))

class CSKHWebHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def _set_headers(self, content_type="application/json", status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)

        # API: Lấy danh sách đơn hàng mẫu
        if parsed_path.path == "/api/orders":
            self._set_headers("application/json")
            self.wfile.write(json.dumps({"success": True, "orders": MOCK_ORDERS_DB}, ensure_ascii=False).encode("utf-8"))
            return

        # API: Lấy danh sách test cases
        if parsed_path.path == "/api/test-cases":
            config_path = os.path.join(BASE_DIR, "config", "test_cases.json")
            tests = []
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    tests = json.load(f)
            self._set_headers("application/json")
            self.wfile.write(json.dumps({"success": True, "test_cases": tests}, ensure_ascii=False).encode("utf-8"))
            return

        # Phục vụ file tĩnh (index.html, style.css, app.js)
        return super().do_GET()

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)

        if parsed_path.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
            except Exception:
                data = {}

            user_query = data.get("query", "").strip()
            mode = data.get("mode", "react")  # 'baseline', 'react', 'autonomous'
            provider_name = data.get("provider", "mock")

            provider = get_llm_provider(provider_name)
            response_data = self.process_ai_query(user_query, mode, provider)

            self._set_headers("application/json")
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))
            return

        self._set_headers("application/json", 404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def process_ai_query(self, user_query: str, mode: str, provider) -> dict:
        """Xử lý truy vấn AI với chế độ Baseline hoặc ReAct Agent."""
        if not user_query:
            return {"success": False, "error": "Vui lòng nhập câu hỏi."}

        steps = []
        final_answer = ""
        query_upper = user_query.upper()

        # CHẾ ĐỘ 1: BASELINE CHATBOT (Không dùng Tool)
        if mode == "baseline":
            llm_res = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
            return {
                "success": True,
                "mode": "baseline",
                "query": user_query,
                "final_answer": llm_res,
                "steps": []
            }

        # CHẾ ĐỘ 2 & 3: REACT AGENT / AUTONOMOUS AGENT (Sử dụng Tools & ReAct Loop)
        # BƯỚC 1: Phân tích intent & chọn Tool
        step1 = {"step": 1, "thought": f"Phân tích yêu cầu khách hàng: '{user_query}'. Cần tra cứu dữ liệu."}
        
        # Nhận diện số điện thoại
        phone_match = None
        for p in ["0901234567", "0988888888", "0912345678"]:
            if p in user_query:
                phone_match = p
                break
        
        # Nhận diện mã đơn
        order_match = None
        for oid in MOCK_ORDERS_DB.keys():
            if oid in query_upper:
                order_match = oid
                break
        if not order_match and any(k in query_upper for k in ["DH", "ORD", "INVALID"]):
            parts = query_upper.replace("#", "").split()
            for part in parts:
                if part.startswith("DH") or part.startswith("ORD") or part.startswith("INVALID"):
                    order_match = part.strip("#,.;:")
                    break

        # Thực thi logic ReAct
        if phone_match:
            step1["action"] = f"search_orders_by_phone['{phone_match}']"
            obs1 = search_orders_by_phone(phone_match)
            step1["observation"] = obs1
            steps.append(step1)

            step2 = {
                "step": 2,
                "thought": f"Đã tìm thấy danh sách đơn hàng cho SĐT {phone_match}. Tổng hợp câu trả lời cho khách.",
                "final_answer": f"Kính chào quý khách! Hệ thống kiểm tra thấy SĐT **{phone_match}** có các đơn hàng:\n\n{obs1}\n\nQuý khách muốn kiểm tra chi tiết hay đổi trả đơn hàng nào, vui lòng phản hồi mã đơn hàng giúp em nhé!"
            }
            steps.append(step2)
            final_answer = step2["final_answer"]

        elif order_match:
            # Tra cứu thông tin đơn hàng
            step1["action"] = f"get_order_details['{order_match}']"
            obs1 = get_order_details(order_match)
            step1["observation"] = obs1
            steps.append(step1)

            if "LỖI" in obs1:
                step2 = {
                    "step": 2,
                    "thought": f"Không tìm thấy mã đơn {order_match} trong hệ thống. Báo lỗi lịch sự và yêu cầu kiểm tra lại.",
                    "final_answer": f"❌ **Không tìm thấy đơn hàng**: Rất tiếc, mã đơn hàng `{order_match}` không tồn tại trên hệ thống của chúng tôi. Quý khách vui lòng kiểm tra lại mã trên hóa đơn hoặc ứng dụng mua hàng giúp em nhé!"
                }
                steps.append(step2)
                final_answer = step2["final_answer"]
            else:
                # Kiểm tra xem có câu hỏi về đổi trả không
                if any(k in query_upper for k in ["ĐỔI", "TRẢ", "HOÀN", "LỖI", "CHẬT"]):
                    step2 = {
                        "step": 2,
                        "thought": f"Khách muốn đổi/trả đơn {order_match}. Tiến hành kiểm tra chính sách và điều kiện đổi trả.",
                        "action": f"check_return_policy['{order_match}', 'Yêu cầu đổi trả từ khách']",
                    }
                    obs2 = check_return_policy(order_match, "Yêu cầu đổi trả từ khách")
                    step2["observation"] = obs2
                    steps.append(step2)

                    if "ĐỦ ĐIỀU KIỆN" in obs2:
                        step3 = {
                            "step": 3,
                            "thought": f"Đơn hàng {order_match} đủ điều kiện. Đưa ra hướng dẫn tạo phiếu đổi trả.",
                            "final_answer": f"✅ **ĐƠN HÀNG ĐỦ ĐIỀU KIỆN ĐỔI TRẢ**\n\n{obs2}\n\n💡 Quý khách có muốn em khởi tạo ngay phiếu đổi trả (Return Ticket) cho đơn hàng `{order_match}` không ạ?"
                        }
                        steps.append(step3)
                        final_answer = step3["final_answer"]
                    else:
                        step3 = {
                            "step": 3,
                            "thought": f"Đơn hàng {order_match} từ chối đổi trả theo quy định.",
                            "final_answer": f"ℹ️ **THÔNG TIN ĐỔI TRẢ ĐƠN HÀNG `{order_match}`**:\n\n{obs2}"
                        }
                        steps.append(step3)
                        final_answer = step3["final_answer"]
                else:
                    step2 = {
                        "step": 2,
                        "thought": f"Đã có chi tiết đơn hàng {order_match}. Đưa ra kết quả cho khách.",
                        "final_answer": f"📦 **KẾT QUẢ TRA CỨU ĐƠN HÀNG `{order_match}`**:\n\n{obs1}\n\nNếu cần hỗ trợ thêm thông tin hoặc muốn đổi trả sản phẩm, quý khách cứ nhắn em nhé!"
                    }
                    steps.append(step2)
                    final_answer = step2["final_answer"]

        else:
            # Không phát hiện mã đơn hay SĐT ➔ Hỏi chính sách chung hoặc xin thông tin
            if any(k in query_upper for k in ["CHÍNH SÁCH", "ĐIỀU KIỆN", "ĐỔI TRẢ", "QUY ĐỊNH"]):
                step1["thought"] = "Khách hỏi chính sách đổi trả chung. Không cần gọi tool tra cứu đơn cụ thể."
                step1["final_answer"] = (
                    "📜 **CHÍNH SÁCH ĐỔI TRẢ HÀNG THƯƠNG MẠI ĐIỆN TỬ**\n\n"
                    "1. **Thời hạn**: Áp dụng trong vòng **7 ngày** kể từ ngày nhận hàng thành công.\n"
                    "2. **Điều kiện**: Sản phẩm còn nguyên tem mác, chưa qua sử dụng hay giặt tẩy.\n"
                    "3. **Lỗi nhà sản xuất**: Miễn phí 100% chi phí vận chuyển đổi trả.\n"
                    "4. **Đổi size / Đổi ý**: Khách hàng hỗ trợ phí ship 2 chiều.\n\n"
                    "👉 Quý khách vui lòng cung cấp **Mã đơn hàng (dạng DHxxxxx)** hoặc **Số điện thoại** để em kiểm tra đơn cụ thể giúp mình ạ!"
                )
                steps.append(step1)
                final_answer = step1["final_answer"]
            else:
                # Dùng LLM Provider sinh câu trả lời CSKH linh hoạt
                llm_response = provider.generate(user_query, system_prompt=REACT_SYSTEM_PROMPT)
                step1["thought"] = "Câu hỏi tổng quát, sử dụng ReAct System Prompt tư vấn CSKH."
                step1["final_answer"] = llm_response
                steps.append(step1)
                final_answer = llm_response

        return {
            "success": True,
            "mode": mode,
            "query": user_query,
            "final_answer": final_answer,
            "steps": steps
        }


def run_server():
    server_address = ("", PORT)
    httpd = socketserver.TCPServer(server_address, CSKHWebHandler)
    print("==========================================================")
    print("🌐 CSKH AI AGENT WEB UI HAS STARTED LOCALLY")
    print(f"🔗 Access Web UI at: http://localhost:{PORT}")
    print("==========================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Web Server Stopped.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()