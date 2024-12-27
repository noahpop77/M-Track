-- Create matchHistory table
CREATE TABLE "matchHistory" (
    "gameID"                VARCHAR(16) NOT NULL,
    "gameVer"               VARCHAR(16) NOT NULL,
    "riotID"                VARCHAR(45) NOT NULL,
    "gameDurationMinutes"   VARCHAR(16) NOT NULL,
    "gameCreationTimestamp" VARCHAR(16) NOT NULL,
    "gameEndTimestamp"      VARCHAR(16) NOT NULL,
    "queueType"             VARCHAR(45) NOT NULL,
    "gameDate"              VARCHAR(45) NOT NULL,
    "participants"          JSON NOT NULL,
    "matchData"             JSON NOT NULL,
    CONSTRAINT unique_pair_index UNIQUE ("gameID", "riotID")
);

-- Create riotIDData table
CREATE TABLE "riotIDData" (
    "riotID" VARCHAR(25) NOT NULL,
    "puuid"  VARCHAR(100) NOT NULL,
    PRIMARY KEY ("riotID")
);

-- Create summonerRankedInfo table
CREATE TABLE "summonerRankedInfo" (
    "encryptedPUUID" VARCHAR(100) NOT NULL,
    "summonerID"     VARCHAR(100) NOT NULL,
    "riotID"         VARCHAR(45) NOT NULL,
    "tier"           VARCHAR(45) NOT NULL,
    "rank"           VARCHAR(45) NOT NULL,
    "leaguePoints"   VARCHAR(45) NOT NULL,
    "queueType"      VARCHAR(45) NOT NULL,
    "wins"           VARCHAR(45) NOT NULL,
    "losses"         VARCHAR(45) NOT NULL,
    PRIMARY KEY ("encryptedPUUID")
);

-- Create user and grant privileges
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'sawa') THEN
        CREATE USER sawa WITH PASSWORD 'sawa';
    END IF;
END $$;
GRANT ALL PRIVILEGES ON DATABASE mtrack TO sawa;
