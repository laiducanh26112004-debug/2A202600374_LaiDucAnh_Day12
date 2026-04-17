// script.js — EduBot frontend connected to RAG Flask API
const API_BASE = "http://localhost:5000/api";

document.addEventListener('DOMContentLoaded', () => {
    const chatBody        = document.getElementById('chat-body');
    const userInput       = document.getElementById('user-input');
    const sendBtn         = document.getElementById('send-btn');
    const suggestionChips = document.querySelectorAll('.chip');
    const refreshBtn      = document.getElementById('refresh-chat');

    let isChatActive = false;

    userInput.focus();
    checkHealth();

    // ── Auto-resize textarea ──────────────────────────────────────────────
    userInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
        sendBtn.classList.toggle('active', this.value.trim() !== '');
        if (this.value === '') this.style.height = 'auto';
    });

    sendBtn.addEventListener('click', handleSend);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
    });

    suggestionChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const t = chip.textContent.trim();
            userInput.value = t.includes('Low Confidence') ? 'Trường nào tốt nhất cho tôi?' : t;
            sendBtn.classList.add('active');
            handleSend();
        });
    });

    refreshBtn.addEventListener('click', resetToHome);

    // ── Health check ──────────────────────────────────────────────────────
    async function checkHealth() {
        try {
            const res  = await fetch(`${API_BASE}/health`);
            const data = await res.json();
            if (data.chunks === 0) {
                showToast('⚠️ Chưa có tài liệu nào trong index. Hãy ingest tài liệu trước.', 'warn');
            } else {
                showToast(`✅ Đã kết nối RAG — ${data.chunks} chunks sẵn sàng`, 'ok');
            }
        } catch {
            showToast('❌ Không kết nối được API server (localhost:5000)', 'error');
        }
    }

    // ── Core send flow ────────────────────────────────────────────────────
    async function handleSend() {
        const text = userInput.value.trim();
        if (!text) return;

        initiateChat();
        userInput.value = '';
        userInput.style.height = 'auto';
        sendBtn.classList.remove('active');

        appendUserMessage(text);
        showTypingIndicator();

        try {
            const res  = await fetch(`${API_BASE}/query`, {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({ question: text, top_k: 5 }),
            });

            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            removeTypingIndicator();
            appendBotMessageComplex(buildResponseObj(data));

        } catch (err) {
            removeTypingIndicator();
            appendBotMessageComplex({
                type: 'low_confidence',
                text: `Không thể kết nối tới API server: ${err.message}. Hãy kiểm tra lại server đang chạy trên port 5000.`,
                alternatives: [
                    'Chạy: python api_server.py',
                    'Kiểm tra GROQ_API_KEY đã export chưa',
                    'Xem log terminal để biết chi tiết lỗi',
                ],
                policyLink: '#',
                citations: {},
            });
        }
    }

    // ── Map API response → display object ────────────────────────────────
    function buildResponseObj(data) {
        const hasCitations = data.citations && Object.keys(data.citations).length > 0;

        if (data.confidence === 'low') {
            return {
                type:         'low_confidence',
                text:         data.answer,
                alternatives: [
                    'Hãy thử đặt câu hỏi cụ thể hơn',
                    'Kiểm tra lại tài liệu đã được nạp chưa',
                    'Tham khảo trực tiếp website tuyển sinh',
                ],
                policyLink: '#',
                citations:  data.citations || {},
            };
        }

        return {
            type:      'normal',
            text:      data.answer,
            citations: data.citations || {},
            source:    hasCitations
                ? buildSourceLabel(data.citations)
                : null,
        };
    }

    // ── Format citation source label from first citation ─────────────────
    function buildSourceLabel(citations) {
        const first = citations[1] || citations[Object.keys(citations)[0]];
        if (!first) return null;
        return {
            id:   first.title || first.source || 'RAG Index',
            date: `Score: ${first.score || '—'}`,
        };
    }

    // ── Layout helpers ────────────────────────────────────────────────────
    function initiateChat() {
        if (isChatActive) return;
        isChatActive = true;
        const inputWrapper = document.getElementById('input-wrapper');
        const chatFooter   = document.getElementById('chat-footer');
        const emptyState   = document.getElementById('empty-state');
        const chatViewport = document.getElementById('chat-viewport');
        const footerNote   = document.getElementById('footer-note');

        emptyState.style.display  = 'none';
        chatViewport.style.display = 'flex';
        chatFooter.style.display  = 'flex';
        chatFooter.insertBefore(inputWrapper, footerNote);
        document.getElementById('suggestion-chips').style.display = 'none';
    }

    function resetToHome() {
        document.querySelectorAll('.message:not(.bot-welcome), .system-alert, .toast-bar')
            .forEach(el => el.remove());

        const chatFooter   = document.getElementById('chat-footer');
        const emptyState   = document.getElementById('empty-state');
        const chatViewport = document.getElementById('chat-viewport');
        const inputWrapper = document.getElementById('input-wrapper');

        chatViewport.style.display = 'none';
        chatFooter.style.display   = 'none';
        emptyState.style.display   = 'flex';
        emptyState.querySelector('.empty-greeting').after(inputWrapper);
        document.getElementById('suggestion-chips').style.display = 'flex';
        isChatActive = false;
        userInput.focus();
    }

    // ── Message renderers ─────────────────────────────────────────────────
    function appendUserMessage(text) {
        const div = document.createElement('div');
        div.className = 'message user-message animate-in';
        div.innerHTML = `
            <div class="message-avatar"><i class="fa-solid fa-user"></i></div>
            <div class="message-wrapper">
                <div class="message-content"><p>${escHtml(text)}</p></div>
            </div>`;
        chatBody.appendChild(div);
        scrollToBottom();
    }

    function appendBotMessageComplex(res) {
        const div = document.createElement('div');
        div.className = 'message bot-message animate-in';

        let contentHtml = '';

        if (res.type === 'normal') {
            // Render answer text (preserve newlines)
            const formattedText = escHtml(res.text).replace(/\n/g, '<br>');
            contentHtml = `<div class="message-origin-text"><p>${formattedText}</p></div>`;

            // Inline citations block
            if (res.citations && Object.keys(res.citations).length > 0) {
                contentHtml += buildCitationBlock(res.citations);
            }

            // Source line
            if (res.source) {
                contentHtml += `
                    <div class="source-info">
                        <i class="fa-solid fa-book-bookmark"></i>
                        Tham chiếu: ${escHtml(res.source.id)} (${escHtml(res.source.date)})
                    </div>`;
            }
        } else if (res.type === 'low_confidence') {
            const altsHtml = res.alternatives.map(a => `<li>${escHtml(a)}</li>`).join('');
            const formattedText = escHtml(res.text).replace(/\n/g, '<br>');
            contentHtml = `
                <div class="validation-notice">
                    <i class="fa-solid fa-triangle-exclamation"></i> Cần xác minh thêm
                </div>
                <div class="message-origin-text"><p>${formattedText}</p></div>
                <div class="related-options">
                    <strong>Gợi ý hướng tiếp cận:</strong>
                    <ul>${altsHtml}</ul>
                    <a href="${res.policyLink}" target="_blank" class="related-link">
                        <i class="fa-solid fa-scale-balanced"></i> Xem chính sách liên quan
                    </a>
                </div>`;
            if (res.citations && Object.keys(res.citations).length > 0) {
                contentHtml += buildCitationBlock(res.citations);
            }
        }

        const actionHtml = `
            <div class="message-actions">
                <button class="action-btn edit-btn" title="Chỉnh sửa"><i class="fa-solid fa-pen"></i> Sửa</button>
                <button class="action-btn report-btn" title="Báo sai"><i class="fa-solid fa-thumbs-down"></i> Báo sai</button>
                <button class="action-btn copy-btn" title="Sao chép"><i class="fa-regular fa-copy"></i></button>
            </div>`;

        div.innerHTML = `
            <div class="message-avatar"><i class="fa-solid fa-bolt"></i></div>
            <div class="message-wrapper">
                <div class="message-content">${contentHtml}</div>
                ${actionHtml}
            </div>`;

        chatBody.appendChild(div);
        bindMessageActions(div, res.text || '');
        scrollToBottom();
    }

    // ── Citation block ────────────────────────────────────────────────────
    function buildCitationBlock(citations) {
        const items = Object.entries(citations).map(([idx, meta]) => `
            <div class="citation-item">
                <span class="citation-index">[${idx}]</span>
                <span class="citation-title">${escHtml(meta.title || '')}</span>
                <span class="citation-source">${escHtml(meta.source || '')}</span>
            </div>`).join('');
        return `<div class="citation-block"><strong>Nguồn tham chiếu:</strong>${items}</div>`;
    }

    // ── Action bindings ───────────────────────────────────────────────────
    function bindMessageActions(msgDiv, rawText) {
        const reportBtn          = msgDiv.querySelector('.report-btn');
        const editBtn            = msgDiv.querySelector('.edit-btn');
        const copyBtn            = msgDiv.querySelector('.copy-btn');
        const msgContentBox      = msgDiv.querySelector('.message-content');
        const originTextContainer = msgDiv.querySelector('.message-origin-text');

        // Copy
        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                navigator.clipboard.writeText(rawText).then(() => {
                    copyBtn.innerHTML = '<i class="fa-solid fa-check"></i>';
                    setTimeout(() => { copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i>'; }, 1500);
                });
            });
        }

        // Report
        if (reportBtn) {
            reportBtn.addEventListener('click', () => {
                if (msgDiv.classList.contains('flagged')) return;
                msgDiv.classList.add('flagged');
                reportBtn.innerHTML = `<i class="fa-solid fa-flag"></i> Đã báo sai`;
                reportBtn.style.color = '#dc2626';

                const alertDiv = document.createElement('div');
                alertDiv.className = 'system-alert animate-in';
                alertDiv.innerHTML = `
                    <i class="fa-solid fa-headset"></i>
                    <span>Đã cắm cờ Policy Mismatch. Đang gọi Tư vấn viên...
                        <i class="fa-solid fa-spinner fa-spin" style="margin-left:4px"></i>
                    </span>`;
                msgDiv.after(alertDiv);
                scrollToBottom();

                setTimeout(() => {
                    alertDiv.classList.add('connected');
                    alertDiv.innerHTML = `<i class="fa-solid fa-user-tie"></i> Tư vấn viên <strong>Ngọc Trâm</strong> đã tham gia đoạn chat.`;
                }, 2500);
            });
        }

        // Edit
        if (editBtn) {
            editBtn.addEventListener('click', () => {
                if (msgContentBox.querySelector('.editor-container')) return;
                const para = originTextContainer?.querySelector('p');
                if (!para) return;

                const plain = para.innerHTML.replace(/<br\s*\/?>/gi, '\n').replace(/<[^>]*>/gm, '');
                originTextContainer.style.display = 'none';

                const editorDiv = document.createElement('div');
                editorDiv.className = 'editor-container animate-in';
                editorDiv.innerHTML = `
                    <textarea class="bot-editor-textarea">${plain.trim()}</textarea>
                    <div class="editor-actions">
                        <button class="cancel-btn">Hủy</button>
                        <button class="save-btn">Lưu sửa</button>
                    </div>`;
                msgContentBox.insertBefore(editorDiv, msgContentBox.firstChild);

                editorDiv.querySelector('.cancel-btn').addEventListener('click', () => {
                    editorDiv.remove();
                    originTextContainer.style.display = 'block';
                });

                editorDiv.querySelector('.save-btn').addEventListener('click', () => {
                    const newText = editorDiv.querySelector('.bot-editor-textarea').value.trim();
                    para.innerHTML = newText.replace(/\n/g, '<br>') +
                        ' <span class="edited-mark">(Đã cập nhật bởi người dùng)</span>';
                    editorDiv.remove();
                    originTextContainer.style.display = 'block';
                    editBtn.disabled = true;
                    editBtn.style.opacity = '0.5';
                });
            });
        }
    }

    // ── Typing indicator ──────────────────────────────────────────────────
    function showTypingIndicator() {
        const div = document.createElement('div');
        div.className = 'message bot-message animate-in typing-msg';
        div.id = 'typing-indicator';
        div.innerHTML = `
            <div class="message-avatar"><i class="fa-solid fa-bolt"></i></div>
            <div class="message-wrapper">
                <div class="message-content">
                    <div class="typing-indicator">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
            </div>`;
        chatBody.appendChild(div);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        document.getElementById('typing-indicator')?.remove();
    }

    // ── Toast notification ────────────────────────────────────────────────
    function showToast(msg, type = 'ok') {
        const existing = document.querySelector('.toast-bar');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = `toast-bar toast-${type}`;
        toast.textContent = msg;
        document.body.appendChild(toast);

        setTimeout(() => toast.classList.add('toast-visible'), 50);
        setTimeout(() => {
            toast.classList.remove('toast-visible');
            setTimeout(() => toast.remove(), 400);
        }, 4000);
    }

    // ── Utilities ─────────────────────────────────────────────────────────
    function scrollToBottom() {
        const vp = document.querySelector('.chat-viewport');
        if (vp) vp.scrollTo({ top: vp.scrollHeight, behavior: 'smooth' });
    }

    function escHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }
});
