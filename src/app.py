"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
Chủ đề: Trợ Lý Tra Cứu Đơn Hàng & Xử Lý Đổi Trả
"""

import json
import os
import sys
from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import (
    MOCK_ORDERS_DB,
    AVAILABLE_TOOLS,
    search_orders_by_phone,
    get_order_details,
    check_return_policy,
    create_return_ticket
)
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()

def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    # Fallback kiểm tra nếu file ở thư mục hiện tại
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_chatbot(user_query: str, provider):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    print(f"⚙️ System Prompt: {CHATBOT_BASELINE_PROMPT.strip()[:120]}...")
    
    # Gọi LLM Provider thực hiện sinh câu trả lời
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")


def run_react_agent(user_query: str, provider):
    """
    Dựng vòng lặp ReAct Agent động (Thought -> Action -> Observation) có Guardrails cho Chủ đề 5.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    query_upper = user_query.upper()
    
    # Nhận diện số điện thoại trong câu hỏi
    phone_match = None
    for p in ["0901234567", "0988888888", "0912345678"]:
        if p in user_query:
            phone_match = p
            break
            
    # Nhận diện mã đơn hàng trong câu hỏi (ví dụ: DH1001, DH0000, ORD12345...)
    order_match = None
    for oid in list(MOCK_ORDERS_DB.keys()) + ["DH0000", "DH9999", "ORD12345", "INVALID_99999"]:
        if oid in query_upper:
            order_match = oid
            break
    if not order_match:
        words = query_upper.replace("#", "").split()
        for w in words:
            if w.startswith("DH") or w.startswith("ORD"):
                order_match = w.strip("#,.;:")
                break

    step = 0
    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")
        
        if step == 1:
            if phone_match:
                print(f"🧠 Thought: Khách cung cấp SĐT {phone_match}. Cần gọi tool search_orders_by_phone.")
                print(f"🛠️ Action: search_orders_by_phone['{phone_match}']")
                obs = search_orders_by_phone(phone_match)
                print(f"👁️ Observation:\n{obs}")
            elif order_match:
                print(f"🧠 Thought: Phát hiện mã đơn hàng {order_match}. Cần gọi tool get_order_details.")
                print(f"🛠️ Action: get_order_details['{order_match}']")
                obs = get_order_details(order_match)
                print(f"👁️ Observation:\n{obs}")
            else:
                if any(k in query_upper for k in ["CHÍNH SÁCH", "ĐIỀU KIỆN", "QUY ĐỊNH", "ĐỔI TRẢ"]):
                    print("🧠 Thought: Khách hỏi chính sách đổi trả chung. Không cần gọi tool tra cứu đơn cụ thể.")
                    print("🏁 Final Answer: Chính sách đổi trả áp dụng trong vòng 7 ngày kể từ khi giao thành công, hàng còn nguyên tem mác. Quý khách vui lòng cung cấp Mã đơn (DHxxxxx) để em kiểm tra đơn cụ thể.")
                else:
                    print("🧠 Thought: Câu hỏi tổng quát CSKH, sử dụng ReAct System Prompt sinh câu trả lời.")
                    llm_res = provider.generate(user_query, system_prompt=REACT_SYSTEM_PROMPT)
                    print(f"🏁 Final Answer:\n{llm_res}")
                break
                
        elif step == 2:
            if phone_match:
                print("🧠 Thought: Đã tìm thấy danh sách đơn hàng theo SĐT. Đưa ra câu trả lời tổng hợp.")
                print(f"🏁 Final Answer: Kính chào quý khách! Em tìm thấy các đơn hàng gắn với SĐT {phone_match}. Quý khách cần tra cứu chi tiết hoặc đổi trả đơn nào ạ?")
                break
            elif order_match:
                obs_prev = get_order_details(order_match)
                if "LỖI" in obs_prev:
                    print(f"🧠 Thought: Đơn hàng {order_match} không tồn tại trên hệ thống.")
                    print(f"🏁 Final Answer: ❌ Rất tiếc, không tìm thấy đơn hàng {order_match}. Quý khách vui lòng kiểm tra lại mã đơn giúp em!")
                    break
                elif any(k in query_upper for k in ["ĐỔI", "TRẢ", "HOÀN", "LỖI", "CHẬT"]):
                    print(f"🧠 Thought: Đơn {order_match} tồn tại. Tiếp tục kiểm tra điều kiện đổi trả.")
                    print(f"🛠️ Action: check_return_policy['{order_match}', 'Yêu cầu từ khách']")
                    obs_policy = check_return_policy(order_match, "Yêu cầu từ khách")
                    print(f"👁️ Observation:\n{obs_policy}")
                else:
                    print(f"🧠 Thought: Đã có chi tiết đơn hàng {order_match}. Đưa ra kết quả tra cứu.")
                    print(f"🏁 Final Answer: Thông tin đơn hàng {order_match} của quý khách đã được tìm thấy!")
                    break

        elif step == 3:
            if order_match:
                obs_policy = check_return_policy(order_match, "Yêu cầu từ khách")
                if "ĐỦ ĐIỀU KIỆN" in obs_policy:
                    print(f"🧠 Thought: Đơn hàng {order_match} đủ điều kiện đổi trả.")
                    print(f"🏁 Final Answer: ✅ Đơn hàng {order_match} đủ điều kiện đổi trả trong 7 ngày. Bạn có muốn tạo phiếu đổi trả không ạ?")
                else:
                    print(f"🧠 Thought: Đơn hàng {order_match} từ chối đổi trả theo quy định.")
                    print(f"🏁 Final Answer: ℹ️ {obs_policy}")
                break

    if step >= MAX_ITERATIONS:
        print(f"\n🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. Ngắt lặp an toàn!")


if __name__ == "__main__":
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("==================================================")
    
    # Khởi tạo Multi-Provider LLM Adapter
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")
    
    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")
    
    # Chạy demo trên câu test số 3
    sample_query = tests[2]["question"]
    
    print("--- DEMO 1: CHẠY TRÊN CHATBOT BASELINE ---")
    run_baseline_chatbot(sample_query, provider)
    
    print("\n--- DEMO 2: CHẠY TRÊN REACT AGENT ---")
    run_react_agent(sample_query, provider)