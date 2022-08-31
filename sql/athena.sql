CREATE EXTERNAL TABLE `student`(
  school_id string,
  student_id_count string, 
  marks_min int, 
  marks_max int, 
  marks_mean int, 
  study_time_in_hr_mean int
)
STORED AS PARQUET
LOCATION 's3://data-bucket-64f4364/student';

CREATE EXTERNAL TABLE IF NOT EXISTS `my-athena-db`.`visitors` (
`visitor_user_agent` string,
`visitor_count` int
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
WITH SERDEPROPERTIES (
'serialization.format' = '1'
) LOCATION 's3://data-bucket-ebf3b62/visitors/'
TBLPROPERTIES ('has_encrypted_data'='false');