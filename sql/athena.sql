CREATE EXTERNAL TABLE `student`(
  school_id string,
  student_id_count string, 
  marks_min int, 
  marks_max int, 
  marks_mean int, 
  study_time_in_hr_mean int
)
STORED AS PARQUET
LOCATION 's3://data-bucket-64f4364/student'