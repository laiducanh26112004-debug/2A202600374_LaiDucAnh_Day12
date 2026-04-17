## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. Vấn đề 1: API key hardcode trong code
2. Vấn đề 2: Không có config management
3. Vấn đề 3: Print thay vì proper logging
4. Vấn đề 4: Không có health check endpoint
5. Vấn đề 5: Port cố định — không đọc từ environment
...
### Exercise 1.3: Comparison table
| Feature       | Basic        | Advanced        | Tại sao quan trọng? |
|--------------|-------------|----------------|---------------------|
| Config       | Hardcode    | Env vars       | Tránh lộ secret, dễ thay đổi theo môi trường (dev/staging/prod) |
| Health check | Không có    | `/health`, `/ready` | Giúp platform (Docker/K8s) biết khi nào app sống và sẵn sàng để restart hoặc route traffic |
| Logging      | print()     | JSON logging   | Dễ monitor, debug, tích hợp log systems và tránh leak thông tin nhạy cảm |
| Shutdown     | Đột ngột    | Graceful       | Tránh mất request đang xử lý, đảm bảo tắt hệ thống an toàn |
...

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
 1. Base image là gì?
FROM python:3.11
Base image là image nền dùng để build container
Ở đây sử dụng Python 3.11 đã được cài sẵn
Mọi thứ trong container sẽ chạy dựa trên image này
 2. Working directory là gì?
WORKDIR /app
Đặt thư mục làm việc bên trong container là /app
Tất cả các lệnh sau (COPY, RUN, CMD) sẽ chạy trong thư mục này
Tương đương với việc chạy cd /app trong terminal
 3. Tại sao COPY requirements.txt trước?
COPY requirements.txt .
RUN pip install -r requirements.txt
 Lý do: Tận dụng Docker cache

Docker build theo từng layer:

Nếu requirements.txt không thay đổi → Docker dùng lại layer cũ
Không cần cài lại dependencies
 Lợi ích:
Build nhanh hơn đáng kể
Tối ưu hiệu năng khi phát triển
 Nếu làm sai:
COPY . .
RUN pip install -r requirements.txt

→ Mỗi lần sửa code → phải cài lại toàn bộ thư viện

 4. CMD vs ENTRYPOINT khác nhau thế nào?
 CMD
CMD ["python", "app.py"]
Lệnh mặc định khi container chạy
Có thể bị override:
docker run my-image python test.py
 ENTRYPOINT
ENTRYPOINT ["python"]
CMD ["app.py"]
ENTRYPOINT: lệnh chính (khó override)
CMD: tham số mặc định
 So sánh nhanh

	CMD	ENTRYPOINT
Mục đích	Lệnh mặc định	Lệnh cố định
Override	Dễ	Khó hơn
Use case	App đơn giản	CLI tool / service
'''
### Exercise 2.3: Image size comparison

- Develop: 1660 MB  
- Production: 236 MB  
- Difference: 85.8%
'''
 ## Part 3: 
 https://github.com/laiducanh26112004-debug/2A202600374_LaiDucAnh_Day12/blob/main/image.png
 https://github.com/laiducanh26112004-debug/2A202600374_LaiDucAnh_Day12/blob/main/image2.png

 ## Part 4:
 https://github.com/laiducanh26112004-debug/2A202600374_LaiDucAnh_Day12/blob/main/image4.png
 https://github.com/laiducanh26112004-debug/2A202600374_LaiDucAnh_Day12/blob/main/image5.png

 ## Part 5:
 ## Part 6:
 https://github.com/laiducanh26112004-debug/2A202600374_LaiDucAnh_Day12/blob/main/image6.png