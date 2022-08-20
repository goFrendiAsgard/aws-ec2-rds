CREATE DATABASE `student`;

CREATE TABLE `student`.`school_tbl` (
  `school_id` varchar(15) NOT NULL,
  `name` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`school_id`)
);


CREATE TABLE `student`.`student_tbl` (
  `student_id` text,
  `first_name` text,
  `last_name` text,
  `gender` text,
  `age` int(11) DEFAULT NULL
);


CREATE TABLE `student`.`study_details_tbl` (
  `school_id` varchar(15) NOT NULL,
  `student_id` varchar(3) NOT NULL,
  `study_time_in_hr` int(11) DEFAULT NULL,
  `health` varchar(15) DEFAULT NULL,
  `internet` varchar(10) DEFAULT NULL,
  `country` varchar(20) DEFAULT NULL,
  `year` varchar(4) DEFAULT NULL,
  `marks` int(11) DEFAULT 0,
  PRIMARY KEY (`school_id`,`student_id`)
) ;
