USE atm_db_s1;

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE transactions;
TRUNCATE TABLE cards;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. INSERT USERS
INSERT INTO users (id, name, dob, phone, citizen_id) VALUES
(1, 'Ngô Zero', '1990-01-01', '0901000000', '001090000000'),
(2, 'Lớt First', '1991-02-02', '0902111111', '001091111111'),
(3, 'Trần Second', '1992-03-03', '0903222222', '001092222222'),
(4, 'Lên Third', '1993-04-04', '0904333333', '001093333333');

-- 2. INSERT CARDS
INSERT INTO cards (number, pin, balance, owner_id) VALUES
('111111', '1234', 50000000, 1),
('222222', '1234', 20000000, 2),
('333333', '1234', 15000000, 3),
('444444', '1234', 10000000, 4);

-- 3. INSERT TRANSACTIONS (Rải đều từ 16/12/2025 đến 18/12/2025)
INSERT INTO transactions (from_card_number, to_card_number, amount, transaction_type, timestamp) VALUES
-- NGÀY 16/12/2025
('111111', '111111', 10000000, 'Deposit',  1765846800), -- 08:00 Sáng
('111111', '222222', 500000,   'Transfer', 1765861200), -- 12:00 Trưa
('222222', '222222', 2000000,  'Deposit',  1765875600), -- 16:00 Chiều
('333333', '111111', 1500000,  'Transfer', 1765890000), -- 20:00 Tối

-- NGÀY 17/12/2025
('111111', '111111', 2000000,  'Withdraw', 1765933200), -- 08:00 Sáng
('444444', '444444', 5000000,  'Deposit',  1765947600), -- 12:00 Trưa
('111111', '333333', 3000000,  'Transfer', 1765962000), -- 16:00 Chiều
('222222', '222222', 1000000,  'Withdraw', 1765976400), -- 20:00 Tối
('111111', '444444', 1000000,  'Transfer', 1765983600), -- 22:00 Khuya

-- NGÀY 18/12/2025 (Hôm nay)
('333333', '333333', 5000000,  'Deposit',  1766019600), -- 08:00 Sáng
('111111', '111111', 500000,   'Withdraw', 1766034000), -- 12:00 Trưa
('222222', '333333', 2500000,  'Transfer', 1766048400), -- 16:00 Chiều
('444444', '111111', 1000000,  'Transfer', 1766062800), -- 20:00 Tối
('111111', '111111', 200000,   'Withdraw', 1766070000); -- 22:00 Khuya