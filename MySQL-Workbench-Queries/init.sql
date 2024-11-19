CREATE DATABASE IF NOT EXISTS `mtrack`;

USE mtrack;

CREATE TABLE `matchHistory`
  (
     `gameID`                VARCHAR(16) NOT NULL,
     `gameVer`               VARCHAR(16) NOT NULL,
     `riotID`                VARCHAR(45) NOT NULL,
     `gameDurationMinutes`   VARCHAR(16) NOT NULL,
     `gameCreationTimestamp` VARCHAR(16) NOT NULL,
     `gameEndTimestamp`      VARCHAR(16) NOT NULL,
     `queueType`             VARCHAR(45) NOT NULL,
     `gameDate`              VARCHAR(45) NOT NULL,
     `participants`          JSON NOT NULL,
     `matchData`             JSON NOT NULL,
     UNIQUE KEY `unique_pair_index` (`gameID`, `riotID`)
  )
engine=innodb
DEFAULT charset=utf8mb4
COLLATE=utf8mb4_0900_ai_ci; 


CREATE TABLE `riotIDData`
  (
     `riotID` VARCHAR(25) NOT NULL,
     `puuid`  VARCHAR(100) NOT NULL,
     PRIMARY KEY (`riotid`)
  )
engine=innodb
DEFAULT charset=utf8mb4
COLLATE=utf8mb4_0900_ai_ci; 


CREATE TABLE `summonerRankedInfo`
  (
     `encryptedPUUID` VARCHAR(100) NOT NULL,
     `summonerID`     VARCHAR(100) NOT NULL,
     `riotID`         VARCHAR(45) NOT NULL,
     `tier`           VARCHAR(45) NOT NULL,
     `rank`           VARCHAR(45) NOT NULL,
     `leaguePoints`   VARCHAR(45) NOT NULL,
     `queueType`      VARCHAR(45) NOT NULL,
     `wins`           VARCHAR(45) NOT NULL,
     `losses`         VARCHAR(45) NOT NULL,
     PRIMARY KEY (`encryptedPUUID`)
  )
engine=innodb
DEFAULT charset=utf8mb4
COLLATE=utf8mb4_0900_ai_ci;

SELECT User, Host FROM mysql.user WHERE User = 'mysql';
UPDATE mysql.user SET Host = '%' WHERE User = 'mysql' AND Host = 'localhost';
FLUSH PRIVILEGES;
CREATE USER 'mysql'@'%' IDENTIFIED BY 'sawa';
FLUSH PRIVILEGES;
GRANT ALL PRIVILEGES ON *.* TO 'mysql'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;

