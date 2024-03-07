
-- 创建 baby_nurse 表
CREATE TABLE baby_nurse (
	id INT PRIMARY KEY,
	name VARCHAR ( 255 ),
	age INT,
	tel VARCHAR ( 255 ),
	address TEXT,
	id_number VARCHAR ( 255 ),
	photo VARCHAR ( 255 )
);
-- 创建 meal_plan 表
CREATE TABLE meal_plan ( meal_plan_id INT PRIMARY KEY, details TEXT, duration INT );
-- 创建 recovery_plan 表
CREATE TABLE recovery_plan ( recovery_plan_id INT PRIMARY KEY, details TEXT, duration INT );


-- 创建 Client 表
CREATE TABLE Client (
	id INT PRIMARY KEY,
	meal_plan_id INT,
	recovery_plan_id INT,
	assigned_baby_nurse INT,
	name VARCHAR ( 255 ) NOT NULL,
	tel VARCHAR ( 255 ) NOT NULL,
	age INT NOT NULL,
	scheduled_date DATE NOT NULL,
	check_in_date DATE ,
	hospital_for_childbirth VARCHAR ( 255 ) NOT NULL,
	contact_name VARCHAR ( 255 ) NOT NULL,
	contact_tel VARCHAR ( 255 ) NOT NULL,
	summary VARCHAR ( 255 ) NOT NULL,
	mode_of_delivery VARCHAR (255) NOT NULL ,
	FOREIGN KEY ( meal_plan_id ) REFERENCES meal_plan ( meal_plan_id ),
	FOREIGN KEY ( recovery_plan_id ) REFERENCES recovery_plan ( recovery_plan_id ),
	FOREIGN KEY ( assigned_baby_nurse ) REFERENCES baby_nurse ( id )
);

-- 创建 Client_Baby_Nurse 表
CREATE TABLE Client_Baby_Nurse (
	id SERIAL PRIMARY KEY,
	client_id INT,
	baby_nurse_id INT,
	start_date DATE NOT NULL,
	end_date DATE NOT NULL,
	status VARCHAR ( 255 ) NOT NULL,
	FOREIGN KEY ( client_id ) REFERENCES Client ( id ),
    FOREIGN KEY ( baby_nurse_id ) REFERENCES baby_nurse ( id )
);
-- 创建 Baby 表
CREATE TABLE Baby (
	id SERIAL PRIMARY KEY,
	client_id INT,
	name VARCHAR ( 255 ) NOT NULL,
	gender CHAR ( 1 ) NOT NULL,
	birth_date DATE NOT NULL,
	birth_weight DECIMAL ( 5, 2 ) NOT NULL,
	birth_height DECIMAL ( 5, 2 ) NOT NULL,
	health_status VARCHAR ( 255 ) NOT NULL,
	birth_certificate VARCHAR ( 255 ) NOT NULL,
	remarks TEXT,
	mom_id_number TEXT NOT NULL,
	dad_id_number TEXT NOT NULL,
	FOREIGN KEY ( client_id ) REFERENCES Client ( id )
);

create table room
(
    id            INTEGER      not null
        primary key,
    status        VARCHAR(255) not null,
    client_id     INTEGER      not null
        references client,
    recently_used VARCHAR(255),
    notes         VARCHAR(255)
);
