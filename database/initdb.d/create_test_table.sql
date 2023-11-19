CREATE DATABASE IF NOT EXISTS assignment_db_test;
USE assignment_db_test;

CREATE TABLE user
(
  id      INT          NULL     AUTO_INCREMENT,
  created timestamp    NULL     COMMENT 'CURRENT_TIMESTAMP',
  name    VARCHAR(100) NULL    ,
  content TEXT         NULL    ,
  PRIMARY KEY (id)
) collate = utf8mb4_bin;