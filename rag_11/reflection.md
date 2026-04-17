# Individual reflection - Lại Đức Anh - 2A202600374

## 1. Role
AI Product Architect + RAG Developer. Phụ trách viết Mini AI Spec (Section 6) và phát triển công cụ RAG (Retrieval-Augmented Generation) cho hệ thống.

## 2. Đóng góp cụ thể
- **Mini AI Spec:** Tổng hợp toàn bộ định hướng sản phẩm từ 5 phần trước thành một bản tóm tắt chiến lược, định nghĩa rõ triết lý "Augmentation" và "Precision-first" để đảm bảo tính nhất quán cho dự án.
- **Phát triển RAG Tool:** Trực tiếp lập trình module truy xuất (retrieval) để AI có thể trích xuất chính xác thông tin từ file Policy thay vì trả lời dựa trên kiến thức cũ của model.
- **Thiết kế cơ chế Trích nguồn:** Đảm bảo mỗi câu trả lời nháp của AI đều đi kèm ID của nguồn chính sách để tư vấn viên đối chiếu nhanh.

## 3. SPEC mạnh/yếu
- **Mạnh nhất:** Phần **Failure Modes** và **Mini Spec**. Nhóm đã xác định được rủi ro "outdated policy" (chính sách cũ) và thiết lập được cơ chế "retrieval-first" để chặn đứng sự tự tin thái quá (hallucination) của AI.
- **Yếu nhất:** Phần **ROI**. Các kịch bản hiện tại chủ yếu thay đổi về quy mô nhân sự (số lượng tư vấn viên). Đáng lẽ nên tách rõ giả định về tỷ lệ chuyển đổi (conversion rate) giữa các kịch bản để thấy được giá trị kinh doanh ngoài việc tiết kiệm thời gian. Data nên được làm sạch và chuẩn bị kĩ hơn để có thể cải thiện việc truy xuất dữ liệu.

## 4. Đóng góp khác
- Xây dựng file `spec.md` cấu trúc chuyên nghiệp, giúp nhóm dễ dàng theo dõi tiến độ các phần.

## 5. Điều học được
- Hiểu sâu sắc sự khác biệt giữa AI hỗ trợ (Augmentation) và AI tự động (Automation). Trong lĩnh vực tuyển sinh, AI đóng vai trò là "trợ lý mẫn cán" tra cứu tài liệu, còn con người đóng vai trò "chốt chặn niềm tin". 
- Nhận ra rằng **Metric là một quyết định về sản phẩm (Product Decision)**: Việc chọn Precision @90% không chỉ là thông số kỹ thuật mà là cam kết về uy tín của tổ chức giáo dục.
- Việc xử lí dữ liệu thô sang dữ liệu sử dụng được là điều vô cùng quan trọng, nên chuyển các định dạng khác nhau về 1 loại duy nhất, dữ liệu nên được làm sạch kĩ, có thể tích hợp các model học máy để hỗ trợ điều này

## 6. Nếu làm lại
- Tôi sẽ dành thêm thời gian để thiết kế phần **Learning Signal** chi tiết hơn, đặc biệt là quy trình tự động hóa việc đưa "Correction Log" ngược trở lại vào Vector Database để cập nhật tri thức ngay lập tức.
- Nên thực hiện User Interview ngắn với một bạn làm tư vấn viên thật để hiểu thực tế họ thường sửa gì trong câu trả lời của AI.
- Xử lí dữ liệu tốt hơn để cải thiện khả năn retrieval của hệ thống RAG

## 7. AI giúp gì / AI sai gì
- **Giúp:** Sử dụng LLM để tóm tắt các phần spec rời rạc thành bản Mini Spec súc tích. AI cũng hỗ trợ viết nhanh các đoạn code boilerplate cho module RAG. Đưa ra các giải pháp cho các vấn đề khi coding.
- **Sai/mislead:** AI đôi khi gợi ý các tính năng quá phức tạp như "tự động gọi điện (voice bot)" – điều này dễ gây lo ngại về đạo đức và vượt quá khả năng xử lý của nhóm trong 48h (Scope creep). Bài học: AI giỏi mở rộng ý tưởng nhưng con người phải là người cắt gọt phạm vi (Scope).
