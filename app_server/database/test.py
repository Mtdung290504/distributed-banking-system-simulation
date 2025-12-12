"""
Test file cho Database class
Chạy: python test.py
"""
import time
from datetime import date
from mysql.connector import Error, IntegrityError, DatabaseError, ProgrammingError

print("🔍 DEBUG: Bắt đầu import Database...")
try:
    from .main import Database
    print("✓ Import Database thành công")
except Exception as e:
    print(f"✗ LỖI IMPORT: {e}")
    import traceback
    traceback.print_exc()
    exit(1)


def print_separator(title: str):
    """In dòng phân cách đẹp"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def handle_exception(e: Exception, context: str) -> str:
    """Xử lý và phân loại exception, trả về mô tả lỗi"""
    if isinstance(e, IntegrityError):
        # Lỗi ràng buộc dữ liệu (trùng lặp, foreign key, etc.)
        return f"[IntegrityError] {e.msg}"
    elif isinstance(e, DatabaseError):
        # Lỗi từ stored procedure hoặc SQL
        return f"[DatabaseError] {e.msg}"
    elif isinstance(e, ProgrammingError):
        # Lỗi cú pháp SQL hoặc procedure không tồn tại
        return f"[ProgrammingError] {e.msg}"
    elif isinstance(e, Error):
        # Lỗi MySQL chung
        return f"[MySQLError] {e.msg}"
    else:
        # Lỗi không xác định
        return f"[UnknownError] {str(e)}"


def test_database():
    """Test toàn bộ các chức năng của Database"""
    
    # Khởi tạo database
    print_separator("KHỞI TẠO DATABASE")
    try:
        db = Database(
            db_url='localhost',
            db_user='root',
            db_password='123456',  # Thay bằng password thực của bạn
            db_name='atm_db_s1'
        )
        print("✓ Kết nối database thành công")
    except ConnectionError as e:
        print(f"✗ LỖI KẾT NỐI: {e}")
        return
    except Error as e:
        print(f"✗ LỖI DATABASE: {handle_exception(e, 'kết nối')}")
        return
    except Exception as e:
        print(f"✗ LỖI KHÔNG XÁC ĐỊNH: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    try:
        writer = db.writer()
        reader = db.reader()
        
        # ============ TEST WRITER ============
        print_separator("TEST WRITER - ĐĂNG KÝ USER")
        
        # Test 1: Đăng ký user mới
        try:
            writer.register_user(
                name='Nguyễn Văn A',
                dob='1990-01-15',
                phone='0912345001',
                citizen_id='001234567001'
            )
            print("✓ Đăng ký user 'Nguyễn Văn A' thành công")
        except IntegrityError as e:
            print(f"✗ Lỗi ràng buộc: {e.msg}")
        except DatabaseError as e:
            print(f"✗ Lỗi database: {e.msg}")
        except Error as e:
            print(f"✗ Lỗi MySQL: {e.msg}")
        except Exception as e:
            print(f"✗ Lỗi không xác định: {str(e)}")
        
        # Test 2: Đăng ký user thứ 2
        try:
            writer.register_user(
                name='Trần Thị B',
                dob='1995-05-20',
                phone='0987654001',
                citizen_id='009876543001'
            )
            print("✓ Đăng ký user 'Trần Thị B' thành công")
        except IntegrityError as e:
            print(f"✗ Lỗi ràng buộc: {e.msg}")
        except DatabaseError as e:
            print(f"✗ Lỗi database: {e.msg}")
        except Error as e:
            print(f"✗ Lỗi MySQL: {e.msg}")
        except Exception as e:
            print(f"✗ Lỗi không xác định: {str(e)}")
        
        # Test 3: Đăng ký user trùng phone (phải lỗi)
        print("\n--- Test trường hợp trùng phone (mong đợi lỗi) ---")
        try:
            writer.register_user(
                name='Lê Văn C',
                dob='1992-03-10',
                phone='0912345001',  # Trùng với user đầu
                citizen_id='001111111111'
            )
            print("✗ KHÔNG NÊN: Đăng ký user trùng phone vẫn thành công!")
        except IntegrityError as e:
            print(f"✓ Đúng: Bắt được IntegrityError - {e.msg}")
        except DatabaseError as e:
            print(f"✓ Đúng: Bắt được DatabaseError - {e.msg}")
        except Error as e:
            print(f"✓ Bắt được lỗi MySQL: {e.msg}")
        except Exception as e:
            print(f"⚠ Lỗi không xác định: {str(e)}")
        
        print_separator("TEST READER - LẤY DANH SÁCH USER")
        
        # Test 4: Lấy tất cả users
        try:
            users = reader.get_all_users()
            print(f"✓ Lấy được {len(users)} users:")
            for user in users:
                print(f"   - ID: {user['id']}, Name: {user['name']}, Phone: {user['phone']}")
        except DatabaseError as e:
            print(f"✗ Lỗi database: {e.msg}")
        except Error as e:
            print(f"✗ Lỗi MySQL: {e.msg}")
        except Exception as e:
            print(f"✗ Lỗi không xác định: {str(e)}")
        
        print_separator("TEST WRITER - ĐĂNG KÝ THẺ")
        
        # Lấy user_id đầu tiên để test
        try:
            users = reader.get_all_users()
        except Exception as e:
            print(f"✗ Không thể lấy danh sách users: {handle_exception(e, 'get_all_users')}")
            users = []
        
        if len(users) > 0:
            test_user_id = users[0]['id']
            
            # Test 5: Đăng ký thẻ cho user
            try:
                writer.register_card(
                    card_number='123456',
                    pin='1234',
                    balance=5000000,
                    user_id=test_user_id
                )
                print(f"✓ Đăng ký thẻ '123456' cho user ID {test_user_id} thành công")
            except IntegrityError as e:
                print(f"✗ Lỗi ràng buộc: {e.msg}")
            except DatabaseError as e:
                print(f"✗ Lỗi database: {e.msg}")
            except Error as e:
                print(f"✗ Lỗi MySQL: {e.msg}")
            except Exception as e:
                print(f"✗ Lỗi không xác định: {str(e)}")
            
            # Test 6: Đăng ký thẻ thứ 2
            try:
                writer.register_card(
                    card_number='654321',
                    pin='4321',
                    balance=3000000,
                    user_id=test_user_id
                )
                print(f"✓ Đăng ký thẻ '654321' cho user ID {test_user_id} thành công")
            except IntegrityError as e:
                print(f"✗ Lỗi ràng buộc: {e.msg}")
            except DatabaseError as e:
                print(f"✗ Lỗi database: {e.msg}")
            except Error as e:
                print(f"✗ Lỗi MySQL: {e.msg}")
            except Exception as e:
                print(f"✗ Lỗi không xác định: {str(e)}")
            
            # Test 7: Đăng ký thẻ trùng số (phải lỗi)
            print("\n--- Test trường hợp trùng số thẻ (mong đợi lỗi) ---")
            try:
                writer.register_card(
                    card_number='123456',  # Trùng
                    pin='9999',
                    balance=1000000,
                    user_id=test_user_id
                )
                print("✗ KHÔNG NÊN: Đăng ký thẻ trùng số vẫn thành công!")
            except IntegrityError as e:
                print(f"✓ Đúng: Bắt được IntegrityError - {e.msg}")
            except DatabaseError as e:
                print(f"✓ Đúng: Bắt được DatabaseError - {e.msg}")
            except Error as e:
                print(f"✓ Bắt được lỗi MySQL: {e.msg}")
            except Exception as e:
                print(f"⚠ Lỗi không xác định: {str(e)}")
            
            print_separator("TEST READER - LẤY DANH SÁCH THẺ")
            
            # Test 8: Lấy danh sách thẻ của user
            try:
                cards = reader.get_cards_by_user_id(test_user_id)
                print(f"✓ User ID {test_user_id} có {len(cards)} thẻ:")
                for card in cards:
                    print(f"   - Số thẻ: {card['number']}, Số dư: {card['balance']:,} VNĐ")
            except DatabaseError as e:
                print(f"✗ Lỗi database: {e.msg}")
            except Error as e:
                print(f"✗ Lỗi MySQL: {e.msg}")
            except Exception as e:
                print(f"✗ Lỗi không xác định: {str(e)}")
            
            print_separator("TEST READER - ĐĂNG NHẬP")
            
            # Test 9: Đăng nhập đúng
            try:
                user_info = reader.login('123456', '1234')
                print(f"✓ Đăng nhập thành công:")
                print(f"   - ID: {user_info['id']}")
                print(f"   - Tên: {user_info['name']}")
                print(f"   - Ngày sinh: {user_info['dob']}")
                print(f"   - Phone: {user_info['phone']}")
                print(f"   - CCCD: {user_info['citizen_id']}")
            except DatabaseError as e:
                print(f"✗ Lỗi database: {e.msg}")
            except Error as e:
                print(f"✗ Lỗi MySQL: {e.msg}")
            except Exception as e:
                print(f"✗ Lỗi không xác định: {str(e)}")
            
            # Test 10: Đăng nhập sai PIN (phải lỗi)
            print("\n--- Test đăng nhập sai PIN (mong đợi lỗi) ---")
            try:
                user_info = reader.login('123456', '9999')
                print("✗ KHÔNG NÊN: Đăng nhập sai PIN vẫn thành công!")
            except DatabaseError as e:
                print(f"✓ Đúng: Bắt được DatabaseError - {e.msg}")
            except Error as e:
                print(f"✓ Bắt được lỗi MySQL: {e.msg}")
            except Exception as e:
                print(f"✓ Bắt được lỗi: {str(e)}")
            
            print_separator("TEST READER - KIỂM TRA SỐ DƯ")
            
            # Test 11: Kiểm tra số dư
            try:
                balance = reader.check_balance('123456')
                print(f"✓ Số dư thẻ '123456': {balance:,} VNĐ")
            except DatabaseError as e:
                print(f"✗ Lỗi database: {e.msg}")
            except Error as e:
                print(f"✗ Lỗi MySQL: {e.msg}")
            except Exception as e:
                print(f"✗ Lỗi không xác định: {str(e)}")
            
            print_separator("TEST WRITER - NẠP TIỀN")
            
            # Test 12: Nạp tiền
            timestamp = int(time.time())
            try:
                writer.deposit_money(
                    card_number='123456',
                    amount=1000000,
                    transaction_time=timestamp
                )
                print(f"✓ Nạp 1,000,000 VNĐ vào thẻ '123456' thành công")
                
                # Kiểm tra số dư sau khi nạp
                new_balance = reader.check_balance('123456')
                print(f"   Số dư mới: {new_balance:,} VNĐ")
            except DatabaseError as e:
                print(f"✗ Lỗi database: {e.msg}")
            except Error as e:
                print(f"✗ Lỗi MySQL: {e.msg}")
            except Exception as e:
                print(f"✗ Lỗi không xác định: {str(e)}")
            
            print_separator("TEST WRITER - RÚT TIỀN")
            
            # Test 13: Rút tiền
            timestamp = int(time.time())
            try:
                writer.withdraw_money(
                    card_number='123456',
                    amount=500000,
                    transaction_time=timestamp
                )
                print(f"✓ Rút 500,000 VNĐ từ thẻ '123456' thành công")
                
                # Kiểm tra số dư sau khi rút
                new_balance = reader.check_balance('123456')
                print(f"   Số dư mới: {new_balance:,} VNĐ")
            except DatabaseError as e:
                print(f"✗ Lỗi database: {e.msg}")
            except Error as e:
                print(f"✗ Lỗi MySQL: {e.msg}")
            except Exception as e:
                print(f"✗ Lỗi không xác định: {str(e)}")
            
            # Test 14: Rút tiền quá số dư (phải lỗi)
            print("\n--- Test rút tiền quá số dư (mong đợi lỗi) ---")
            timestamp = int(time.time())
            try:
                writer.withdraw_money(
                    card_number='123456',
                    amount=999999999,
                    transaction_time=timestamp
                )
                print("✗ KHÔNG NÊN: Rút tiền quá số dư vẫn thành công!")
            except DatabaseError as e:
                print(f"✓ Đúng: Bắt được DatabaseError - {e.msg}")
            except Error as e:
                print(f"✓ Bắt được lỗi MySQL: {e.msg}")
            except Exception as e:
                print(f"✓ Bắt được lỗi: {str(e)}")
            
            print_separator("TEST WRITER - CHUYỂN KHOẢN")
            
            # Test 15: Chuyển khoản
            timestamp = int(time.time())
            try:
                balance_before_from = reader.check_balance('123456')
                balance_before_to = reader.check_balance('654321')
                
                writer.transfer_money(
                    from_card_number='123456',
                    to_card_number='654321',
                    amount=200000,
                    transaction_time=timestamp
                )
                print(f"✓ Chuyển 200,000 VNĐ từ '123456' sang '654321' thành công")
                
                balance_after_from = reader.check_balance('123456')
                balance_after_to = reader.check_balance('654321')
                
                print(f"   Thẻ '123456': {balance_before_from:,} → {balance_after_from:,} VNĐ")
                print(f"   Thẻ '654321': {balance_before_to:,} → {balance_after_to:,} VNĐ")
            except DatabaseError as e:
                print(f"✗ Lỗi database: {e.msg}")
            except Error as e:
                print(f"✗ Lỗi MySQL: {e.msg}")
            except Exception as e:
                print(f"✗ Lỗi không xác định: {str(e)}")
            
            # Test 16: Chuyển khoản cho chính mình (phải lỗi)
            print("\n--- Test chuyển khoản cho chính mình (mong đợi lỗi) ---")
            timestamp = int(time.time())
            try:
                writer.transfer_money(
                    from_card_number='123456',
                    to_card_number='123456',
                    amount=100000,
                    transaction_time=timestamp
                )
                print("✗ KHÔNG NÊN: Chuyển khoản cho chính mình vẫn thành công!")
            except DatabaseError as e:
                print(f"✓ Đúng: Bắt được DatabaseError - {e.msg}")
            except Error as e:
                print(f"✓ Bắt được lỗi MySQL: {e.msg}")
            except Exception as e:
                print(f"✓ Bắt được lỗi: {str(e)}")
            
            # Test 17: Chuyển khoản đến thẻ không tồn tại (phải lỗi)
            print("\n--- Test chuyển đến thẻ không tồn tại (mong đợi lỗi) ---")
            timestamp = int(time.time())
            try:
                writer.transfer_money(
                    from_card_number='123456',
                    to_card_number='999999',
                    amount=100000,
                    transaction_time=timestamp
                )
                print("✗ KHÔNG NÊN: Chuyển đến thẻ không tồn tại vẫn thành công!")
            except DatabaseError as e:
                print(f"✓ Đúng: Bắt được DatabaseError - {e.msg}")
            except Error as e:
                print(f"✓ Bắt được lỗi MySQL: {e.msg}")
            except Exception as e:
                print(f"✓ Bắt được lỗi: {str(e)}")
            
            print_separator("TEST WRITER - ĐỔI PIN")
            
            # Test 18: Đổi PIN
            try:
                writer.change_pin(
                    card_number='123456',
                    new_pin='5678'
                )
                print(f"✓ Đổi PIN thẻ '123456' thành công")
                
                # Thử đăng nhập với PIN mới
                user_info = reader.login('123456', '5678')
                print(f"   Đăng nhập với PIN mới thành công!")
            except DatabaseError as e:
                print(f"✗ Lỗi database: {e.msg}")
            except Error as e:
                print(f"✗ Lỗi MySQL: {e.msg}")
            except Exception as e:
                print(f"✗ Lỗi không xác định: {str(e)}")
            
            # Test 19: Đổi PIN trùng PIN cũ (phải lỗi)
            print("\n--- Test đổi PIN trùng PIN cũ (mong đợi lỗi) ---")
            try:
                writer.change_pin(
                    card_number='123456',
                    new_pin='5678'  # Trùng PIN hiện tại
                )
                print("✗ KHÔNG NÊN: Đổi PIN trùng PIN cũ vẫn thành công!")
            except DatabaseError as e:
                print(f"✓ Đúng: Bắt được DatabaseError - {e.msg}")
            except Error as e:
                print(f"✓ Bắt được lỗi MySQL: {e.msg}")
            except Exception as e:
                print(f"✓ Bắt được lỗi: {str(e)}")
            
            print_separator("TEST READER - LỊCH SỬ GIAO DỊCH")
            
            # Test 20: Lấy lịch sử giao dịch
            try:
                transactions = reader.get_transaction_history('123456')
                print(f"✓ Thẻ '123456' có {len(transactions)} giao dịch:")
                for i, txn in enumerate(transactions, 1):
                    print(f"   {i}. {txn['transaction_type']}: {txn['amount']:,} VNĐ")
                    print(f"      Từ: {txn['from_card_number']} → Đến: {txn['to_card_number']}")
                    print(f"      Thời gian: {txn['timestamp']}")
            except DatabaseError as e:
                print(f"✗ Lỗi database: {e.msg}")
            except Error as e:
                print(f"✗ Lỗi MySQL: {e.msg}")
            except Exception as e:
                print(f"✗ Lỗi không xác định: {str(e)}")
            
            print_separator("TỔNG KẾT")
            print("✓ Đã test hoàn tất tất cả các chức năng!")
            print("✓ Các test case bao gồm:")
            print("   - Writer: register_user, register_card, deposit_money,")
            print("             withdraw_money, transfer_money, change_pin")
            print("   - Reader: get_all_users, get_cards_by_user_id, login,")
            print("             check_balance, get_transaction_history")
            print("   - Edge cases: trùng lặp, số dư không đủ, thẻ không tồn tại, etc.")
            print("   - Exception handling: IntegrityError, DatabaseError, MySQLError, Unknown")
        
        else:
            print("✗ Không có user nào để test các chức năng tiếp theo")
    
    except Exception as e:
        print(f"\n✗ LỖI NGHIÊM TRỌNG KHÔNG BẮT ĐƯỢC: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Đóng kết nối
        print_separator("ĐÓNG KẾT NỐI")
        try:
            db.close()
            print("✓ Đã đóng kết nối database")
        except Exception as e:
            print(f"⚠ Lỗi khi đóng kết nối: {str(e)}")


if __name__ == '__main__':
    test_database()