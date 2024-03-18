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

INSERT INTO baby_nurse (baby_nurse_id, name, age, tel, address, id_number, photo) VALUES (1, 'Jane Doe', 32, '555-1234', '123 Main St, Anytown', 'ID12345678', 'photo_url_1');
INSERT INTO baby_nurse (baby_nurse_id, name, age, tel, address, id_number, photo) VALUES (2, 'Emily Jones', 28, '555-5678', '456 Oak St, Sometown', 'ID87654321', 'photo_url_2');
INSERT INTO baby_nurse (baby_nurse_id, name, age, tel, address, id_number, photo) VALUES (3, 'Sarah Brown', 35, '555-9012', '789 Pine St, Yourtown', 'ID23456789', 'photo_url_3');
INSERT INTO baby_nurse (baby_nurse_id, name, age, tel, address, id_number, photo) VALUES (4, 'Fiona Smith', 29, '555-3456', '321 Elm St, Theirtown', 'ID34567890', 'photo_url_4');
INSERT INTO baby_nurse (baby_nurse_id, name, age, tel, address, id_number, photo) VALUES (5, 'Linda White', 40, '555-7890', '654 Cedar St, Hertown', 'ID45678901', 'photo_url_5');



-- 注意：这里假设client表中至少有两个客户，其ID分别为1和2。


INSERT INTO client (
    id,
    meal_plan_id,
    recovery_plan_id,
    assigned_baby_nurse,
    name,
    tel,
    age,
    scheduled_date,
    check_in_date,
    hospital_for_childbirth,
    contact_name,
    contact_tel,
    mode_of_delivery,
    room
) VALUES (
    1,
    1, -- 假设meal_plan表中的ID
    1, -- 假设recovery_plan表中的ID
    1, -- 假设baby_nurse表中的ID
    '张三',
    '12345678901',
    28,
    '2024-06-01',
    '2024-06-02',
    '市第一医院',
    '李四',
    '10987654321',
    '顺产',
    NULL
);

INSERT INTO client (
    id,
    meal_plan_id,
    recovery_plan_id,
    assigned_baby_nurse,
    name,
    tel,
    age,
    scheduled_date,
    check_in_date,
    hospital_for_childbirth,
    contact_name,
    contact_tel,
    mode_of_delivery,
    room
) VALUES (
    2,
    2, -- 假设meal_plan表中的ID
    2, -- 假设recovery_plan表中的ID
    2, -- 假设baby_nurse表中的ID
    '王五',
    '12312312345',
    30,
    '2024-07-10',
    '2024-07-12',
    '市第二医院',
    '赵六',
    '5432154321',
    '剖宫产',
    NULL
);

-- 请根据实际情况调整meal_plan_id, recovery_plan_id和assigned_baby_nurse的值
-- 如果相关的外键表（meal_plan, recovery_plan, baby_nurse）还没有被创建或还没有数据
-- 你需要先为它们添加相应的记录或在这里使用NULL或有效的默认值
INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (1, '8001', '0', NULL, '2024-03-01', '需要额外的床单');

INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (2, '8002', '0', NULL, NULL, '刚刚装修过');

INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (3, '8003', '0', NULL, '2024-03-05', '需要婴儿床');

INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (4, '8004', '0', NULL, NULL, '更换空调系统');

INSERT INTO room (id, room_number, status, client_id, recently_used, notes)
VALUES (5, '8005', '0', NULL, NULL, '靠近电梯');

