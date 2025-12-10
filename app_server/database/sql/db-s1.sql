DROP DATABASE IF EXISTS atm_db_s1;
CREATE DATABASE IF NOT EXISTS atm_db_s1 CHARACTER SET UTF8 COLLATE utf8_vietnamese_ci;
USE atm_db_s1;

CREATE TABLE IF NOT EXISTS users(
    id INT AUTO_INCREMENT PRIMARY KEY,	
    name NVARCHAR(255) NOT NULL,		        -- Tên người dùng
    dob DATE NOT NULL,					        -- Ngày tháng năm sinh
    phone VARCHAR(11) NOT NULL UNIQUE,			-- Số điện thoại
    citizen_id CHAR(12) NOT NULL UNIQUE	        -- Số căn cước công dân (CCCD)
);

CREATE TABLE cards (
    number CHAR(6) NOT NULL PRIMARY KEY,					-- Số tài khoản, dùng 6 ký tự để đơn giản hóa khi kiểm thử
    pin CHAR(4) NOT NULL,									-- Mã PIN, dùng 4 ký tự để đơn giản hóa khi kiểm thử
    balance BIGINT UNSIGNED NOT NULL CHECK(balance >= 0),	-- Số dư hiện tại (không được âm, ràng buộc CHECK) - ĐÃ SỬA: >= 0

    owner_id INT NOT NULL,									-- ID của người sở hữu thẻ (khóa ngoại tham chiếu tới bảng users)
    FOREIGN KEY (owner_id) REFERENCES users(id)				-- Khóa ngoại tham chiếu tới cột id trong bảng users
);

CREATE TABLE transactions (
    from_card_number CHAR(6) NOT NULL,									-- Số tài khoản nguồn (khóa ngoại tham chiếu tới bảng cards)
    to_card_number CHAR(6) NOT NULL,									-- Số tài khoản đích (khóa ngoại tham chiếu tới bảng cards)
    amount INT UNSIGNED NOT NULL CHECK(amount > 0),						-- Số tiền giao dịch (không được âm, ràng buộc CHECK)
    transaction_type ENUM('Withdraw', 'Deposit', 'Transfer') NOT NULL,	-- Loại giao dịch (rút tiền, gửi tiền, chuyển khoản)
    timestamp BIGINT DEFAULT (UNIX_TIMESTAMP()),						-- Thời gian giao dịch (timestamp dạng số nguyên)
    FOREIGN KEY (from_card_number) REFERENCES cards(number),			-- Khóa ngoại tham chiếu tới số tài khoản nguồn
    FOREIGN KEY (to_card_number) REFERENCES cards(number)				-- Khóa ngoại tham chiếu tới số tài khoản đích
);