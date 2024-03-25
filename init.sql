-- 月子套餐
create table meal_plan
(
    meal_plan_id serial
        primary key,
    details      text,
    duration     integer
);

alter table meal_plan
    owner to postgres;

-- 产康套餐

create table recovery_plan
(
    recovery_plan_id serial
        primary key,
    details          text,
    duration         integer
);

alter table recovery_plan
    owner to postgres;




INSERT INTO meal_plan (meal_plan_id, details, duration) VALUES (1, 'Low Carb Plan for 30 Days', 30);
INSERT INTO meal_plan (meal_plan_id, details, duration) VALUES (2, 'Vegan Wellness Plan, Full of Greens', 15);
INSERT INTO meal_plan (meal_plan_id, details, duration) VALUES (3, 'High Protein Plan for Muscle Building', 60);
INSERT INTO meal_plan (meal_plan_id, details, duration) VALUES (4, 'Detox and Cleanse 10-Day Plan', 10);
INSERT INTO meal_plan (meal_plan_id, details, duration) VALUES (5, 'Mediterranean Diet Plan for Heart Health', 45);

INSERT INTO recovery_plan (recovery_plan_id, details, duration) VALUES (1, 'Post-surgery Recovery Plan, Focused on Mobility', 30);
INSERT INTO recovery_plan (recovery_plan_id, details, duration) VALUES (2, 'Mental Health Wellness Plan, Stress Reduction', 60);
INSERT INTO recovery_plan (recovery_plan_id, details, duration) VALUES (3, 'Sports Injury Recovery Plan, Emphasis on Physical Therapy', 45);
INSERT INTO recovery_plan (recovery_plan_id, details, duration) VALUES (4, 'Post-pregnancy Recovery Plan, Strengthening Core', 90);
INSERT INTO recovery_plan (recovery_plan_id, details, duration) VALUES (5, 'Chronic Pain Management Plan, Holistic Approach', 120);

INSERT INTO baby_nurse (baby_nurse_id, name, age, tel, address, id_number, childcare_certificate) VALUES (1, 'Jane Doe', 32, '555-1234', '123 Main St, Anytown', 'ID12345678', 'photo_url_1');
INSERT INTO baby_nurse (baby_nurse_id, name, age, tel, address, id_number, childcare_certificate) VALUES (2, 'Emily Jones', 28, '555-5678', '456 Oak St, Sometown', 'ID87654321', 'photo_url_2');
INSERT INTO baby_nurse (baby_nurse_id, name, age, tel, address, id_number, childcare_certificate) VALUES (3, 'Sarah Brown', 35, '555-9012', '789 Pine St, Yourtown', 'ID23456789', 'photo_url_3');
INSERT INTO baby_nurse (baby_nurse_id, name, age, tel, address, id_number, childcare_certificate) VALUES (4, 'Fiona Smith', 29, '555-3456', '321 Elm St, Theirtown', 'ID34567890', 'photo_url_4');
INSERT INTO baby_nurse (baby_nurse_id, name, age, tel, address, id_number, childcare_certificate) VALUES (5, 'Linda White', 40, '555-7890', '654 Cedar St, Hertown', 'ID45678901', 'photo_url_5');



-- 注意：这里假设client表中至少有两个客户，其ID分别为1和2。


-- INSERT INTO client (
--     id,
--     meal_plan_id,
--     recovery_plan_id,
--     assigned_baby_nurse,
--     name,
--     tel,
--     age,
--     scheduled_date,
--     check_in_date,
--     hospital_for_childbirth,
--     contact_name,
--     contact_tel,
--     mode_of_delivery,
--     room
-- ) VALUES (
--     1,
--     1, -- 假设meal_plan表中的ID
--     1, -- 假设recovery_plan表中的ID
--     1, -- 假设baby_nurse表中的ID
--     '张三',
--     '12345678901',
--     28,
--     '2024-06-01',
--     '2024-06-02',
--     '市第一医院',
--     '李四',
--     '10987654321',
--     '顺产',
--     NULL
-- );

-- INSERT INTO client (id, meal_plan_id, recovery_plan_id, assigned_baby_nurse, name, tel, age, scheduled_date, check_in_date, hospital_for_childbirth, contact_name, contact_tel, mode_of_delivery, room, id_number) VALUES
-- (20, 1, 1, 1, '张三', '12345678901', 30, '2024-04-01', '2024-04-10', '北方医院', '李四', '19876543211', '顺产', '8011', '220104197001011234'),
-- (21, 2, 2, 2, '李四', '12345678902', 28, '2024-04-02', '2024-04-11', '南方医院', '王五', '19876543212', '剖宫产', '8002', '220104197001011235'),
-- (22, 3, 3, 3, '王五', '12345678903', 32, '2024-04-03', '2024-04-12', '东方医院', '张三', '19876543213', '顺产', '8003', '220104197001011236'),
-- (23, 4, 4, 4, '赵六', '12345678904', 29, '2024-04-04', '2024-04-13', '西方医院', '李四', '19876543214', '剖宫产', '8004', '220104197001011237'),
-- (24, 5, 5, 5, '周七', '12345678905', 31, '2024-04-05', '2024-04-14', '中央医院', '王五', '19876543215', '顺产', '8005', '220104197001011238'),
-- (25, 1, 1, 1, '吴八', '12345678906', 33, '2024-04-06', '2024-04-15', '北方医院', '张三', '19876543216', '剖宫产', '8006', '220104197001011239'),
-- (26, 2, 2, 2, '郑九', '12345678907', 27, '2024-04-07', '2024-04-16', '南方医院', '李四', '19876543217', '顺产', '8007', '220104197001011240'),
-- (27, 3, 3, 3, '黄十', '12345678908', 34, '2024-04-08', '2024-04-17', '东方医院', '王五', '19876543218', '剖宫产', '8008', '220104197001011241'),
-- (28, 4, 4, 4, '曹十一', '12345678909', 30, '2024-04-09', '2024-04-18', '西方医院', '张三', '19876543219', '顺产', '8009', '220104197001011242'),
-- (29, 5, 5, 5, '钱十二', '12345678910', 35, '2024-04-10', '2024-04-19', '中央医院', '李四', '19876543220', '剖宫产', '8010', '220104197001');

-- INSERT INTO client (id, meal_plan_id, recovery_plan_id, assigned_baby_nurse, name, tel, age, scheduled_date, check_in_date, hospital_for_childbirth, contact_name, contact_tel, mode_of_delivery, room, id_number) VALUES
-- (30, 1, 1, 1, '孙十三', '12345678911', 36, '2024-04-11', '2024-04-20', '北方医院', '赵六', '19876543221', '顺产', '8010', '220104197001011244'),
-- (31, 2, 2, 2, '李十四', '12345678912', 29, '2024-04-12', '2024-04-21', '南方医院', '周七', '19876543222', '剖宫产', '8010', '220104197001011245'),
-- (32, 3, 3, 3, '王十五', '12345678913', 37, '2024-04-13', '2024-04-22', '东方医院', '吴八', '19876543223', '顺产', '8010', '220104197001011246'),
-- (33, 4, 4, 4, '赵十六', '12345678914', 28, '2024-04-14', '2024-04-23', '西方医院', '郑九', '19876543224', '剖宫产', '8010', '220104197001011247'),
-- (34, 5, 5, 5, '周十七', '12345678915', 39, '2024-04-15', '2024-04-24', '中央医院', '黄十', '19876543225', '顺产', '8010', '220104197001011248'),
-- (35, 1, 1, 1, '吴十八', '12345678916', 27, '2024-04-16', '2024-04-25', '北方医院', '曹十一', '19876543226', '剖宫产', '8010', '220104197001011249'),
-- (36, 2, 2, 2, '郑十九', '12345678917', 38, '2024-04-17', '2024-04-26', '南方医院', '钱十二', '19876543227', '顺产', '8010', '220104197001011250'),
-- (37, 3, 3, 3, '黄二十', '12345678918', 26, '2024-04-18', '2024-04-27', '东方医院', '孙十三', '19876543228', '剖宫产', '8010', '220104197001011251'),
-- (38, 4, 4, 4, '曹二十一', '12345678919', 40, '2024-04-19', '2024-04-28', '西方医院', '李十四', '19876543229', '顺产', '8010', '220104197001011252'),
-- (39, 5, 5, 5, '钱二十二', '12345678920', 25, '2024-04-20', '2024-04-29', '中央医院', '王十五', '19876543230', '剖宫产', '8010', '220104197001011253');

-- INSERT INTO client (id, meal_plan_id, recovery_plan_id, assigned_baby_nurse, name, tel, age, scheduled_date, check_in_date, hospital_for_childbirth, contact_name, contact_tel, mode_of_delivery, room, id_number) VALUES
-- (41, 2, 2, 2, '李二十四', '12345678922', 32, '2024-05-02', '2024-05-11', '南方医院', '周十七', '19876543232', '剖宫产', '8002', '220104197001011255'),
-- (42, 3, 3, 3, '王二十五', '12345678923', 33, '2024-05-03', '2024-05-12', '东方医院', '吴十八', '19876543233', '顺产', '8002', '220104197001011256'),
-- (43, 4, 4, 4, '赵二十六', '12345678924', 34, '2024-05-04', '2024-05-13', '西方医院', '郑十九', '19876543234', '剖宫产', '8002', '220104197001011257'),
-- (44, 5, 5, 5, '周二十七', '12345678925', 35, '2024-05-05', '2024-05-14', '中央医院', '黄二十', '19876543235', '顺产', '8002', '220104197001011258'),
-- (45, 1, 1, 1, '吴二十八', '12345678926', 36, '2024-05-06', '2024-05-15', '北方医院', '曹二十一', '19876543236', '剖宫产', '8002', '220104197001011259'),
-- (46, 2, 2, 2, '郑二十九', '12345678927', 37, '2024-05-07', '2024-05-16', '南方医院', '钱二十二', '19876543237', '顺产', '8002', '220104197001011260'),
-- (47, 3, 3, 3, '黄三十', '12345678928', 38, '2024-05-08', '2024-05-17', '东方医院', '孙二十三', '19876543238', '剖宫产', '8002', '220104197001011261'),
-- (48, 4, 4, 4, '曹三十一', '12345678929', 39, '2024-05-09', '2024-05-18', '西方医院', '李二十四', '19876543239', '顺产', '8002', '220104197001011262'),
-- (49, 5, 5, 5, '钱三十二', '12345678930', 40, '2024-05-10', '2024-05-19', '中央医院', '王二十五', '19876543240', '剖宫产', '8002', '220104197001011263'),
-- (50, 1, 1, 1, '孙三十三', '12345678931', 41, '2024-05-11', '2024-05-20', '北方医院', '赵二十六', '19876543241', '顺产', '8002', '220104197001011264');



-- 请根据实际情况调整meal_plan_id, recovery_plan_id和assigned_baby_nurse的值
-- 如果相关的外键表（meal_plan, recovery_plan, baby_nurse）还没有被创建或还没有数据
-- 你需要先为它们添加相应的记录或在这里使用NULL或有效的默认值
INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (1, '8001', '0', NULL, NULL, NULL);

INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (2, '8002', '0', NULL, NULL, NULL);

INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (3, '8003', '0', NULL, NULL, NULL);

INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (4, '8004', '0', NULL, NULL, NULL);

INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (5, '8005', '0', NULL, NULL, NULL);

INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (6, '8006', '0', NULL, NULL,NULL);

INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (7, '8007', '0', NULL, NULL, NULL);
INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (8, '8008', '0', NULL, NULL, NULL);
INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (9, '8009', '0', NULL, NULL, NULL);
INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (10, '8010', '0', NULL, NULL, NULL);
INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (11, '8011', '0', NULL, NULL, NULL);
INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (12, '8012', '0', NULL, NULL, NULL);
INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (13, '8013', '0', NULL, NULL, NULL);
INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (14, '8014', '0', NULL, NULL, NULL);
INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (15, '8015', '0', NULL, NULL, NULL);
INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (16, '8016', '0', NULL, NULL, NULL);
INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (17, '8017', '0', NULL, NULL, NULL);
INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (18, '8018', '0', NULL, NULL, NULL);
INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (19, '8019', '0', NULL, NULL, NULL);
INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (20, '8020', '0', NULL, NULL, NULL);
