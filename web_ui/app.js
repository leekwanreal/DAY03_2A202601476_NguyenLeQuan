/**
 * 🚀 APP.JS - CSKH AI AGENT INTERACTIVE FRONTEND LOGIC
 */

document.addEventListener("DOMContentLoaded", () => {
    const modeSelect = document.getElementById("modeSelect");
    const currentModeLabel = document.getElementById("currentModeLabel");

    modeSelect.addEventListener("change", () => {
        const val = modeSelect.value;
        if (val === "react") {
            currentModeLabel.innerText = "Chế độ: ReAct Agent (Thought ➔ Action ➔ Observation ➔ Final Answer)";
        } else if (val === "baseline") {
            currentModeLabel.innerText = "Chế độ: Baseline Chatbot (Không sử dụng Tool)";
        } else {
            currentModeLabel.innerText = "Chế độ: Autonomous Goal Agent (Multi-step Planning)";
        }
    });
});

function usePrompt(text) {
    const userInput = document.getElementById("userInput");
    userInput.value = text;
    userInput.focus();
}

function clearChat() {
    const chatMessages = document.getElementById("chatMessages");
    chatMessages.innerHTML = `
        <div class="message system-msg">
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="msg-content">
                <h4>Đã xóa lịch sử trò chuyện.</h4>
                <p>Tôi sẵn sàng hỗ trợ bạn tra cứu đơn hàng mới!</p>
            </div>
        </div>
    `;
}

async function handleSend(event) {
    event.preventDefault();
    const userInput = document.getElementById("userInput");
    const query = userInput.value.strip ? userInput.value.strip() : userInput.value.trim();
    if (!query) return;

    const mode = document.getElementById("modeSelect").value;
    const provider = document.getElementById("providerSelect").value;
    const chatMessages = document.getElementById("chatMessages");

    // 1. Render User Message
    const userMsgHtml = `
        <div class="message user-msg">
            <div class="avatar"><i class="fa-solid fa-user"></i></div>
            <div class="msg-content">
                <p>${escapeHtml(query)}</p>
            </div>
        </div>
    `;
    chatMessages.insertAdjacentHTML("beforeend", userMsgHtml);
    userInput.value = "";
    scrollToBottom();

    // 2. Render Loading Indicator
    const loadingId = "loading-" + Date.now();
    const loadingHtml = `
        <div class="message ai-msg" id="${loadingId}">
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="msg-content">
                <p><i class="fa-solid fa-spinner fa-spin"></i> Đang suy luận và tra cứu dữ liệu...</p>
            </div>
        </div>
    `;
    chatMessages.insertAdjacentHTML("beforeend", loadingHtml);
    scrollToBottom();

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query, mode, provider })
        });
        const data = await response.json();

        // Remove Loading Indicator
        const loadingElem = document.getElementById(loadingId);
        if (loadingElem) loadingElem.remove();

        if (data.success) {
            renderAiResponse(data);
        } else {
            renderErrorMessage(data.error || "Đã xảy ra lỗi hệ thống.");
        }
    } catch (err) {
        const loadingElem = document.getElementById(loadingId);
        if (loadingElem) loadingElem.remove();
        renderErrorMessage("Không thể kết nối đến Web Server Backend. Vui lòng kiểm tra lại server.py.");
    }
}

function renderAiResponse(data) {
    const chatMessages = document.getElementById("chatMessages");

    let traceHtml = "";
    if (data.steps && data.steps.length > 0) {
        traceHtml += `
            <div class="react-trace-box">
                <div class="trace-header">
                    <span><i class="fa-solid fa-microchip"></i> Tiến trình ReAct Loop (${data.steps.length} bước)</span>
                    <i class="fa-solid fa-chevron-down"></i>
                </div>
                <div class="trace-steps">
        `;

        data.steps.forEach(step => {
            traceHtml += `<div class="step-card">`;
            if (step.thought) {
                traceHtml += `<div class="step-thought"><strong>🧠 Thought (Bước ${step.step}):</strong> ${escapeHtml(step.thought)}</div>`;
            }
            if (step.action) {
                traceHtml += `<div class="step-action"><strong>🛠️ Action:</strong> <code>${escapeHtml(step.action)}</code></div>`;
            }
            if (step.observation) {
                traceHtml += `<div class="step-obs"><strong>👁️ Observation:</strong>\n${escapeHtml(step.observation)}</div>`;
            }
            traceHtml += `</div>`;
        });

        traceHtml += `
                </div>
            </div>
        `;
    }

    const formattedAnswer = formatMarkdownText(data.final_answer);

    const aiMsgHtml = `
        <div class="message ai-msg">
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="msg-content">
                ${traceHtml}
                <div class="final-answer-box">
                    ${formattedAnswer}
                </div>
            </div>
        </div>
    `;

    chatMessages.insertAdjacentHTML("beforeend", aiMsgHtml);
    scrollToBottom();
}

function renderErrorMessage(errorText) {
    const chatMessages = document.getElementById("chatMessages");
    const errorHtml = `
        <div class="message ai-msg">
            <div class="avatar" style="background: var(--danger);"><i class="fa-solid fa-triangle-exclamation"></i></div>
            <div class="msg-content" style="border-color: rgba(239,68,68,0.4);">
                <p style="color: #fca5a5;"><strong>Lỗi:</strong> ${escapeHtml(errorText)}</p>
            </div>
        </div>
    `;
    chatMessages.insertAdjacentHTML("beforeend", errorHtml);
    scrollToBottom();
}

function scrollToBottom() {
    const chatMessages = document.getElementById("chatMessages");
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(str) {
    if (!str) return "";
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function formatMarkdownText(text) {
    if (!text) return "";
    let html = escapeHtml(text);
    // Format bold
    html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    // Format code block
    html = html.replace(/`(.*?)`/g, "<code>$1</code>");
    // Format line breaks
    html = html.replace(/\n/g, "<br>");
    return html;
}