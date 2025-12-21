## Mô tả:

## Chạy code:

```bash
# Chạy client:
py -m app_client.main
# Chạy client 2:
py -m z_app_client.main
```

```bash
# Chạy server:
py -m app_server.main
# Chạy server 2:
py -m z_app_server.main
```

## Phụ thuộc:

- mysql-connector-python

## Notes:

- Type check: python.analysis.typeCheckingMode
- Nhớ đổi IP trong config
- Server 2 kết nối đến database có tên đuôi s2, tạo database với tên đuôi s2 nếu chạy server 2