# JobLens — Đọc hiểu tin tuyển dụng

Dán một tin tuyển dụng tiếng Việt, rồi hỏi về những yêu cầu trong đó. Trợ lý có thể tách kỹ năng bắt buộc, kỹ năng được ưu tiên, nơi làm việc và các thông tin cần chú ý. Bạn có thể hỏi tiếp trong cùng cuộc trao đổi.

Bản này chỉnh từ ví dụ Chatbot của Streamlit. Luồng chat được giữ đơn giản; phần thay đổi chính là câu chữ trên màn hình và lời hướng dẫn mô hình đọc tin tuyển dụng bằng tiếng Việt.

## Chạy ứng dụng

Cài Python 3.12. Trên Windows, chạy `CAI_DAT.bat`, sau đó mở `CHAY_DEMO.bat`.

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Ứng dụng cần kết nối một mô hình thật để trả lời. Với thiết lập mặc định, cài [Ollama](https://ollama.com/download), mở terminal và tải mô hình:

```bash
ollama pull qwen2.5:1.5b
```

Giữ Ollama hoạt động, rồi mở lại ứng dụng. Lần tải đầu cần mạng và dung lượng để lưu mô hình. Sau đó có thể chạy trên máy của bạn.

Nếu dùng dịch vụ khác, điền địa chỉ máy chủ, tên mô hình và khóa truy cập trong phần bên trái. Dịch vụ đó phải hỗ trợ cách gọi tương thích OpenAI. Phí sử dụng phụ thuộc dịch vụ bạn chọn.

## Thử với một tin ngắn

“Công ty Sen tuyển thực tập sinh AI tại Hà Nội. Yêu cầu biết Python và Git cơ bản; có SQL là lợi thế. Không yêu cầu kinh nghiệm. Làm việc từ thứ Hai đến thứ Sáu.”

Bạn có thể hỏi: “Kỹ năng nào bắt buộc và kỹ năng nào chỉ được ưu tiên?”

Mô hình được yêu cầu trả lời bằng tiếng Việt và ghi rõ thông tin chưa được nêu. Nó vẫn có thể hiểu sai, nên bạn cần đối chiếu lại với tin gốc.

## Đọc code từ đâu?

Mở `app.py`. Phần đầu tạo các ô kết nối, tiếp theo lưu nội dung cuộc trao đổi, rồi gửi câu hỏi đến mô hình khi người dùng nhập tin.

Bản này không huấn luyện LLM và không có kết quả trả lời mẫu được dùng thay cho mô hình thật. Các kiểm tra tự động chỉ kiểm tra luồng giao diện với phản hồi giả lập, chưa đánh giá chất lượng trả lời của mô hình.

Xem [NGUON.md](NGUON.md) để đối chiếu ví dụ gốc và phần đã chỉnh. Giữ giấy phép Apache 2.0 của Streamlit.
