USE atm_db_s1;

DROP PROCEDURE IF EXISTS register_user;
DROP PROCEDURE IF EXISTS register_card;
DROP PROCEDURE IF EXISTS get_all_users;
DROP PROCEDURE IF EXISTS get_cards_by_user_id;
DROP PROCEDURE IF EXISTS withdraw_money;
DROP PROCEDURE IF EXISTS transfer_money;
DROP PROCEDURE IF EXISTS deposit_money;
DROP PROCEDURE IF EXISTS change_pin;
DROP PROCEDURE IF EXISTS login;
DROP PROCEDURE IF EXISTS check_balance;
DROP PROCEDURE IF EXISTS get_transaction_history;

-- ĐĂNG KÝ USER (ADMIN)
DELIMITER //
CREATE PROCEDURE register_user(
    IN user_name NVARCHAR(255),
    IN user_dob DATE,
    IN user_phone VARCHAR(11),
    IN user_citizen_id CHAR(12)
)
BEGIN
    -- Kiểm tra trùng lặp số điện thoại hoặc CCCD
    IF EXISTS (SELECT 1 FROM users WHERE phone = user_phone OR citizen_id = user_citizen_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Số điện thoại hoặc CCCD đã tồn tại.';
    END IF;

    -- Thêm người dùng mới
    INSERT INTO users (name, dob, phone, citizen_id)
    VALUES (user_name, user_dob, user_phone, user_citizen_id);
END //
DELIMITER ;

-- ĐĂNG KÝ THẺ CHO USER (ADMIN)
DELIMITER //
CREATE PROCEDURE register_card(
    IN card_number CHAR(6),
    IN card_pin CHAR(4),
    IN card_balance BIGINT,
    IN user_id INT
)
BEGIN
    -- Kiểm tra tồn tại số thẻ hoặc người dùng
    IF EXISTS (SELECT 1 FROM cards WHERE number = card_number) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Số thẻ đã tồn tại.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM users WHERE id = user_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Người dùng không tồn tại.';
    END IF;

    -- Thêm thẻ mới
    INSERT INTO cards (number, pin, balance, owner_id)
    VALUES (card_number, card_pin, card_balance, user_id);
END //
DELIMITER ;

-- LẤY DANH SÁCH USER (ADMIN)
DELIMITER //
CREATE PROCEDURE get_all_users()
BEGIN
    SELECT id, name, dob, phone, citizen_id
    FROM users
    ORDER BY id ASC;
END //
DELIMITER ;

-- LẤY DANH SÁCH THẺ CỦA MỘT USER (ADMIN)
DELIMITER //
CREATE PROCEDURE get_cards_by_user_id(
    IN user_id INT
)
BEGIN
    -- Kiểm tra nếu người dùng không tồn tại
    IF NOT EXISTS (SELECT 1 FROM users WHERE id = user_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Người dùng không tồn tại.';
    END IF;

    -- Lấy danh sách thẻ
    SELECT number, pin, balance
    FROM cards
    WHERE owner_id = user_id
    ORDER BY number ASC;
END //
DELIMITER ;

-- RÚT TIỀN
DELIMITER //
CREATE PROCEDURE withdraw_money(
    IN card_number CHAR(6),
    IN amount INT UNSIGNED,
    IN transaction_time BIGINT  -- Thời gian giao dịch dạng timestamp từ Python
)
BEGIN
    DECLARE current_balance BIGINT UNSIGNED;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION -- Xử lý lỗi (Rollback nếu có lỗi)
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION; -- Bắt đầu Transaction

    -- 1. Lấy số dư hiện tại
    SELECT balance INTO current_balance
    FROM cards
    WHERE number = card_number;

    -- 2. Kiểm tra nếu số dư không đủ
    IF current_balance < amount THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Số dư hiện tại không đủ.';
    END IF;

    -- 3. Thực hiện rút tiền
    UPDATE cards
    SET balance = balance - amount
    WHERE number = card_number;

    -- 4. Ghi vào lịch sử giao dịch
    INSERT INTO transactions (from_card_number, to_card_number, amount, transaction_type, timestamp)
    VALUES (card_number, card_number, amount, 'Withdraw', transaction_time);

    COMMIT; -- Kết thúc Transaction
END //
DELIMITER ;

-- CHUYỂN KHOẢN
DELIMITER //
CREATE PROCEDURE transfer_money(
    IN from_card_number CHAR(6),
    IN to_card_number CHAR(6),
    IN amount INT UNSIGNED,
    IN transaction_time BIGINT -- Thời gian giao dịch dạng timestamp từ Python
)
BEGIN
    DECLARE from_balance BIGINT UNSIGNED;
    DECLARE to_card_exists TINYINT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION; -- Bắt đầu Transaction

    -- 1. Kiểm tra không chuyển khoản cho chính mình
    IF from_card_number = to_card_number THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Không thể chuyển khoản cho chính mình.';
    END IF;

    -- 2. Kiểm tra tài khoản đích có tồn tại không
    SELECT COUNT(*) INTO to_card_exists
    FROM cards
    WHERE number = to_card_number;

    IF to_card_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Số tài khoản đối ứng không tồn tại.';
    END IF;

    -- 3. Lấy số dư tài khoản nguồn
    SELECT balance INTO from_balance
    FROM cards
    WHERE number = from_card_number;

    -- 4. Kiểm tra nếu số dư không đủ
    IF from_balance < amount THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Số dư hiện tại không đủ.';
    END IF;

    -- 5. Thực hiện chuyển tiền
    UPDATE cards
    SET balance = balance - amount
    WHERE number = from_card_number;

    UPDATE cards
    SET balance = balance + amount
    WHERE number = to_card_number;

    -- 6. Ghi vào lịch sử giao dịch
    INSERT INTO transactions (from_card_number, to_card_number, amount, transaction_type, timestamp)
    VALUES (from_card_number, to_card_number, amount, 'Transfer', transaction_time);

    COMMIT; -- Kết thúc Transaction
END //
DELIMITER ;

-- NẠP TIỀN/GỬI TIỀN
DELIMITER //
CREATE PROCEDURE deposit_money(
    IN card_number CHAR(6),
    IN amount INT UNSIGNED,
    IN transaction_time BIGINT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- 1. Kiểm tra tài khoản đích có tồn tại không
    -- Gần như không bao giờ xảy ra tại tầng ứng dụng, nhưng để tránh sai xót khi code thao tác raw
    IF NOT EXISTS (SELECT 1 FROM cards WHERE number = card_number) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Số thẻ không tồn tại.';
    END IF;

    -- 2. Thực hiện nạp tiền
    UPDATE cards
    SET balance = balance + amount
    WHERE number = card_number;

    -- 3. Ghi vào lịch sử giao dịch
    INSERT INTO transactions (from_card_number, to_card_number, amount, transaction_type, timestamp)
    VALUES (card_number, card_number, amount, 'Deposit', transaction_time);

    COMMIT;
END //
DELIMITER ;

-- ĐỔI MÃ PIN
DELIMITER //
CREATE PROCEDURE change_pin(
    IN card_number CHAR(6),
    IN new_pin CHAR(4)
)
BEGIN
    DECLARE current_pin CHAR(4);

    -- Lấy mã PIN hiện tại
    SELECT pin INTO current_pin
    FROM cards
    WHERE number = card_number;

    -- Kiểm tra mã PIN mới không được trùng mã PIN cũ
    IF current_pin = new_pin THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Mã PIN mới không được trùng với mã PIN cũ.';
    END IF;

    -- Thực hiện đổi mã PIN
    UPDATE cards
    SET pin = new_pin
    WHERE number = card_number;
END //
DELIMITER ;

-- ĐĂNG NHẬP
DELIMITER //
CREATE PROCEDURE login(
    IN card_number CHAR(6),
    IN card_pin CHAR(4),
    OUT user_id INT,
    OUT user_name NVARCHAR(255),
    OUT user_dob DATE,
    OUT user_phone VARCHAR(11),
    OUT user_citizen_id CHAR(12)
)
BEGIN
    -- Kiểm tra thẻ và mã PIN
    IF NOT EXISTS (SELECT 1 FROM cards WHERE number = card_number AND pin = card_pin) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Số thẻ hoặc mã PIN không hợp lệ.';
    END IF;

    -- Lấy thông tin người dùng
    SELECT u.id, u.name, u.dob, u.phone, u.citizen_id
    INTO user_id, user_name, user_dob, user_phone, user_citizen_id
    FROM users u
    JOIN cards c ON u.id = c.owner_id
    WHERE c.number = card_number;
END //
DELIMITER ;

-- KIỂM TRA SỐ DƯ
DELIMITER //
CREATE PROCEDURE check_balance(
    IN card_number CHAR(6)
)
BEGIN
    -- Lấy số dư
    SELECT balance
    FROM cards
    WHERE number = card_number;
END //
DELIMITER ;

-- LẤY LỊCH SỬ GIAO DỊCH
DELIMITER //
CREATE PROCEDURE get_transaction_history(
    IN card_number CHAR(6)
)
BEGIN
    -- Lấy lịch sử giao dịch
    SELECT *
    FROM transactions
    WHERE from_card_number = card_number OR to_card_number = card_number
    ORDER BY timestamp DESC;
END //
DELIMITER ;