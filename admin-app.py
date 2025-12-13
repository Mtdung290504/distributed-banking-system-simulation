# File này hỗ trợ tạo user/thẻ và thử nghiệm
# Không liên quan đến chương trình chính

from mysql.connector import Error as SQLException

from app_server.database.main import Database
from shared.utils import now, dmy_from_date, dmy_hms_from_timestamp

databases = [
    Database("127.0.0.1", "root", "123456", f"atm_db_{s_name}")
    for s_name in ["s1", "s2"]
]
print("Kết nối đến server thành công!")
print("Nhập lệnh (lệnh, tham_số_1, tham_số_2,...). Nhập 'exit' để thoát.")

while True:
    try:
        command = input(">> ")
    except EOFError:
        break

    if command.strip().lower() == "exit":
        print("Đang thoát...")
        break

    # Xử lý lệnh từ input
    parts = command.split(",", 1)

    if len(parts) < 1 or not parts[0].strip():
        print("Lệnh không hợp lệ!")
        continue

    method_name = parts[0].strip()

    # Tách các tham số và loại bỏ khoảng trắng thừa
    params = []
    if len(parts) > 1:
        raw_params = parts[1].split(",")
        params = [p.strip() for p in raw_params]

    try:
        if method_name == "register-user":
            if len(params) != 4:
                print("Số lượng tham số không đúng (cần: name, dob, phone, citizenID)")
                continue

            for database in databases:
                database.writer().register_user(
                    params[0], params[1], params[2], params[3]
                )

            print("Đăng ký người dùng thành công!")

        elif method_name == "register-card":
            if len(params) != 4:
                print(
                    "Số lượng tham số không đúng (cần: cardNumber, pin, balance, userId)"
                )
                continue

            for database in databases:
                database.writer().register_card(
                    params[0], params[1], int(params[2]), int(params[3])
                )

            print("Đăng ký thẻ thành công!")

        elif method_name == "withdraw":
            if len(params) != 2:
                print("Số lượng tham số không đúng (cần: cardNumber, amount)")
                continue

            for database in databases:
                database.writer().withdraw_money(params[0], int(params[1]), now())

            print("Rút tiền thành công!")

        elif method_name == "deposit":
            if len(params) != 2:
                print("Số lượng tham số không đúng (cần: cardNumber, amount)")
                continue

            for database in databases:
                database.writer().deposit_money(params[0], int(params[1]), now())

            print("Nạp tiền thành công!")

        elif method_name == "transfer":
            if len(params) != 3:
                print("Số lượng tham số không đúng (cần: fromCard, toCard, amount)")
                continue
            for database in databases:
                database.writer().transfer_money(
                    params[0], params[1], int(params[2]), now()
                )
            print("Chuyển tiền thành công!")

        elif method_name == "history-of":
            if len(params) != 1:
                print("Số lượng tham số không đúng (cần: cardNumber)")
                continue

            for database in databases:
                print("DB:", database.db_name)
                transactions = database.reader().get_transaction_history(params[0])
                for transaction in [
                    {**t, "timestamp": dmy_hms_from_timestamp(t["timestamp"])}
                    for t in transactions
                ]:
                    print(transaction)

        elif method_name == "list-user":
            for database in databases:
                print("DB:", database.db_name)
                users = database.reader().get_all_users()
                for user in [{**u, "dob": dmy_from_date(u["dob"])} for u in users]:
                    print(user)

        elif method_name == "cards-of":
            if len(params) != 1:
                print("Số lượng tham số không đúng (cần: userId)")
                continue

            for database in databases:
                print("DB:", database.db_name)
                cards = database.reader().get_cards_by_user_id(int(params[0]))
                for c in cards:
                    print(c)

        elif method_name == "balance-of":
            if len(params) != 1:
                print("Số lượng tham số không đúng (cần: cardNumber)")
                continue

            for database in databases:
                print("DB:", database.db_name)
                balance = database.reader().check_balance(params[0])
                print(f"Số dư: {balance}")

        elif method_name == "change-pin-of":
            if len(params) != 2:
                print("Số lượng tham số không đúng (cần: cardNumber, newPin)")
                continue

            for database in databases:
                database.writer().change_pin(params[0], params[1])

            print("Đổi PIN thành công!")

        else:
            print(f"Không tìm thấy lệnh: {method_name}")

    # Ép kiểu fail
    except ValueError as e:
        print(f"Lỗi định dạng số: {e}")

    except SQLException as e:
        if e.sqlstate == "45000" and e.msg:
            custom_message = e.msg
            print(custom_message)
        else:
            # Lỗi SQL hệ thống khác (ví dụ: mất kết nối, lỗi cú pháp...)
            print(f"Lỗi hệ thống trong DB: {e.msg} (Code: {e.errno})")

    except Exception as e:
        # Các lỗi khác
        print(f"Lỗi khi gọi lệnh: {e}")
