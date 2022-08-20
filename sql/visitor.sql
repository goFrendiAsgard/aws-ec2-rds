USE appdb;
DROP TABLE IF EXISTS `visitors`;
CREATE TABLE `visitors` (
  `visitor_id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `visitor_ip` VARCHAR(32) NOT NULL,
  `visitor_user_agent` VARCHAR(500) NOT NULL,
  `visitor_date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`visitor_id`)
) ENGINE=INNODB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

insert into visitors(visitor_ip, visitor_user_agent) VALUES 
    ('10.10.10.10', 'lynx')
    , ('10.10.10.11', 'chrome')
    , ('10.10.10.11', 'firefox')
    , ('10.10.10.11', 'chrome');