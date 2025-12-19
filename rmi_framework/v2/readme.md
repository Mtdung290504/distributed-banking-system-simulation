## Giới hạn của Framework

### So với Java RMI

Framework này là phiên bản đơn giản hóa cho mục đích học tập, chưa đầy đủ như Java RMI:

- Không có Distributed Garbage Collection (DGC) để tự động dọn dẹp remote objects
- Không có dynamic class loading
- Không có activation framework
- Chưa hỗ trợ bảo mật giao tiếp

### Các tính năng được hỗ trợ

**Type Safety & Validation:**

- Hỗ trợ type hints để gợi ý code khi gọi remote methods
- Nhưng **quan trọng**, các tham số truyền vào remote methods phải tuân theo quy tắc của xml-rpc
- Kiểm tra tương thích interface giữa client và server thông qua hash
- Validate tham số trước khi gọi remote method
- Bắt buộc remote objects phải kế thừa từ Remote interface

**Registry Management:**

- Chỉ hỗ trợ 1 local registry duy nhất trên mỗi process để đơn giản hóa và tránh nhầm lẫn
- Nếu cần nhiều registries phải chạy trong các process hoặc máy khác nhau
- Hỗ trợ bind, unbind, rebind và lookup services

**Callback Support:**

Framework hỗ trợ callback theo 2 cách:

- Pass RemoteObject làm tham số khi gọi remote method: Framework tự động export object vào local registry, server nhận được stub và gọi callback như hàm thường. Object được track với exported_name để có thể unbind sau.

- Return RemoteObject từ remote method: Hàm trên server return về TRỰC TIẾP một RemoteObject thì framework tự động serialize, client nhận stub để gọi methods trên server.

**Giới hạn quan trọng về callback:**

- Chỉ hỗ trợ pass hoặc return RemoteObject trực tiếp
- Không hỗ trợ RemoteObject lồng sâu trong dict, list, hoặc custom objects
- Ví dụ: không thể pass dict chứa RemoteObject làm value, hoặc list chứa các RemoteObject

**Memory Management:**

- Chưa có cơ chế auto cleanup: RemoteObjects được auto-export sẽ tồn tại trong registry cho đến khi manually unbind, Python GC thu hồi object, hoặc registry shutdown
- Nên luôn unbind callback thủ công khi không cần nữa để tránh memory leak

**Thread Safety:**

- Registry operations, Object ID generation an toàn với multi-threading
- XML-RPC server xử lý concurrent requests

### Khuyến nghị sử dụng

**Chỉ dùng cho:**

- Đồ án và học tập để hiểu cơ chế RMI
- Demo các tính năng distributed computing cơ bản
- Các bài toán client-server đơn giản
