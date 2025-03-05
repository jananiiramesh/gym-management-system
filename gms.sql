DROP DATABASE IF EXISTS gym_management;
CREATE DATABASE gym_management;
USE gym_management;
DROP TABLE IF EXISTS Member;
DROP TABLE IF EXISTS Membership;
DROP TABLE IF EXISTS Workout_plan;
DROP TABLE IF EXISTS Exercises;
DROP TABLE IF EXISTS Diet_plan;
DROP TABLE IF EXISTS Meal_plan;
DROP TABLE IF EXISTS Instructor;
DROP TABLE IF EXISTS Equipment;
DROP TABLE IF EXISTS Payment;
DROP TABLE IF EXISTS Schedule;
DROP TABLE IF EXISTS Progress;
DROP TABLE IF EXISTS Equipment_info;
DROP TABLE IF EXISTS Admin;
DROP TABLE IF EXISTS Roles;

CREATE TABLE Admin (
	admin_id SERIAL PRIMARY KEY,
    username VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(20) NOT NULL,
    role_id INT NOT NULL DEFAULT 1,
    CHECK (username LIKE "AD%")
);

CREATE TABLE Member (
	member_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    password VARCHAR(10) NOT NULL,
    dob DATE NOT NULL,
    phone_number VARCHAR(10) NOT NULL,
    gender CHAR(1) NOT NULL,
    role_id INT NOT NULL DEFAULT 2
);

CREATE TABLE Instructor (
	instructor_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    password VARCHAR(10) NOT NULL,
    specialization VARCHAR(20) NOT NULL,
    years_of_experience INT,
    gender CHAR(1) NOT NULL,
    role_id INT NOT NULL DEFAULT 3
);

CREATE TABLE Equipment (
	equipment_id INT PRIMARY KEY auto_increment NOT NULL,
    name VARCHAR(30) UNIQUE NOT NULL,
    equipment_status ENUM('WORKING FINE','REQUIRES MAINTENANCE')
);

CREATE TABLE Membership (
	membership_id INT PRIMARY KEY,
    member_id VARCHAR(20) UNIQUE NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    type VARCHAR(10) NOT NULL,
    FOREIGN KEY (member_id) REFERENCES Member(member_id) ON DELETE CASCADE
);

CREATE TABLE Payment (
	payment_id INT PRIMARY KEY auto_increment,
    member_id VARCHAR(20) UNIQUE NOT NULL,
    amount DECIMAL(5,2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    FOREIGN KEY(member_id) REFERENCES Member(member_id) ON DELETE CASCADE
);

CREATE TABLE Workout_plan (
	workout_id INT PRIMARY KEY auto_increment,
    member_id VARCHAR(20) UNIQUE NOT NULL,
    instructor_id VARCHAR(20) NOT NULL,
    FOREIGN KEY (member_id) REFERENCES Member(member_id) ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES Instructor(instructor_id) ON DELETE CASCADE
);

CREATE TABLE Exercises (
	exercise_id INT PRIMARY KEY auto_increment,
    workout_id INT NOT NULL,
    day VARCHAR(10) NOT NULL,
    exercise_name VARCHAR(30) NOT NULL,
    sets INT NOT NULL,
    reps INT NOT NULL,
    FOREIGN KEY (workout_id) REFERENCES Workout_plan(workout_id) ON DELETE CASCADE
);

CREATE TABLE Diet_plan (
	diet_id INT PRIMARY KEY auto_increment,
    member_id VARCHAR(20) UNIQUE NOT NULL,
    instructor_id VARCHAR(20) NOT NULL,
    FOREIGN KEY (member_id) REFERENCES Member(member_id) ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES Instructor(instructor_id) ON DELETE CASCADE
);

CREATE TABLE Meal_plan (
	meal_id INT PRIMARY KEY auto_increment,
    diet_id INT NOT NULL,
    day_of_week ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday') NOT NULL,
    meal_of_day ENUM('Breakfast','Lunch','Dinner') NOT NULL,
    description TEXT,
    calories INT,
    FOREIGN KEY (diet_id) REFERENCES Diet_plan(diet_id) ON DELETE CASCADE,
    UNIQUE(diet_id, day_of_week, meal_of_day)
);

CREATE TABLE Schedule (
	schedule_id INT PRIMARY KEY auto_increment,
    instructor_id VARCHAR(20) NOT NULL,
    member_id VARCHAR(20) NOT NULL,
    day ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday') NOT NULL,
    start_time TIME NOT NULL CHECK (start_time BETWEEN '06:00:00' AND '22:00:00'),
    end_time TIME NOT NULL CHECK (end_time BETWEEN '06:00:00' AND '22:00:00'),
    FOREIGN KEY (instructor_id) REFERENCES Instructor(instructor_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES Member(member_id) ON DELETE CASCADE
);

CREATE TABLE Progress (
	progress_id INT PRIMARY KEY auto_increment,
    member_id VARCHAR(20) UNIQUE,
    date_progress DATE NOT NULL,
    weight DECIMAL(3,2) NOT NULL,
    water_percentage DECIMAL(3,2) NOT NULL,
    protein_percentage DECIMAL(3,2) NOT NULL,
    fitness_level INT NOT NULL CHECK (fitness_level BETWEEN 10 AND 100),
    FOREIGN KEY (member_id) REFERENCES Member(member_id) ON DELETE CASCADE
);

CREATE TABLE Equipment_info (
	info_id INT PRIMARY KEY auto_increment,
    equipment_id INT NOT NULL,
    description TEXT,
    target_body_part VARCHAR(20),
    FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id) ON DELETE CASCADE
);

DELIMITER //
CREATE TRIGGER member_id_check
BEFORE INSERT ON Member
FOR EACH ROW
BEGIN
    IF NEW.member_id NOT LIKE 'ME%' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: member_id must start with "ME"';
    END IF;
END //

DELIMITER ;

DELIMITER //
CREATE TRIGGER check_gender_mem
BEFORE INSERT ON Member
FOR EACH ROW
BEGIN
    IF NEW.gender NOT IN ('M', 'F') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: gender must be either "M" or "F"';
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_gender_update_mem
BEFORE UPDATE ON Member
FOR EACH ROW
BEGIN
    IF NEW.gender NOT IN ('M', 'F') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: gender must be either "M" or "F"';
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER instructor_id_check
BEFORE INSERT ON Instructor
FOR EACH ROW
BEGIN
    IF NEW.instructor_id NOT LIKE 'IN%' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: instructor_id must start with "IN"';
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_gender_ins
BEFORE INSERT ON Instructor
FOR EACH ROW
BEGIN
    IF NEW.gender NOT IN ('M', 'F') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: gender must be either "M" or "F"';
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_gender_update_ins
BEFORE UPDATE ON Instructor
FOR EACH ROW
BEGIN
    IF NEW.gender NOT IN ('M', 'F') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: gender must be either "M" or "F"';
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_membership
BEFORE INSERT ON Membership
FOR EACH ROW
BEGIN
	IF NEW.type NOT IN ('GENERAL', 'PERSONAL') THEN
		SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Membership type must be either "General" or "Personal"';
	END IF;
END //
DELIMITER //

DELIMITER //
CREATE TRIGGER check_membership_update
BEFORE UPDATE ON Membership
FOR EACH ROW
BEGIN
	IF NEW.type NOT IN ('GENERAL', 'PERSONAL') THEN
		SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Membership type must be either "General" or "Personal"';
	END IF;
END //
DELIMITER //

DELIMITER //
CREATE TRIGGER check_payment_method
BEFORE INSERT ON Payment
FOR EACH ROW
BEGIN
	IF NEW.payment_method NOT IN ('UPI','CASH','CARD','CHEQUE') THEN
		SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Invalid Payment method';
	END IF;
END //
DELIMITER //

DELIMITER //
CREATE TRIGGER check_payment_method_update
BEFORE UPDATE ON Payment
FOR EACH ROW
BEGIN
	IF NEW.payment_method NOT IN ('UPI','CASH','CARD','CHEQUE') THEN
		SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Invalid Payment method';
	END IF;
END //
DELIMITER //

DELIMITER //
CREATE TRIGGER check_day
BEFORE INSERT ON Exercises
FOR EACH ROW
BEGIN
	IF NEW.day NOT IN ('MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY','SUNDAY') THEN
		SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Error: Invalid day';
	END IF;
END //
DELIMITER //

DELIMITER //
CREATE TRIGGER check_day_update
BEFORE UPDATE ON Exercises
FOR EACH ROW
BEGIN
	IF NEW.day NOT IN ('MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY','SUNDAY') THEN
		SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Error: Invalid day';
	END IF;
END //
DELIMITER //
    








