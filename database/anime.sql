CREATE DATABASE anime_db;
USE anime_db;

-- Table 1: Users
CREATE TABLE Users (
    user_id INT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    gender ENUM('Male', 'Female', 'Non-Binary','Other'),
    birthday DATE DEFAULT NULL,
    place VARCHAR(50),
    joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    days_watched FLOAT
);

-- Table 2: Anime Information 
CREATE TABLE Anime_Information (
    anime_id INT PRIMARY KEY AUTO_INCREMENT,
    anime_name VARCHAR(255) NOT NULL,
    english_name VARCHAR(255),
    other_name VARCHAR(255),
    synopsis TEXT,
    type_anime VARCHAR(20),
    genres VARCHAR(255)
);

-- Table 3: Anime Scores
CREATE TABLE Anime_Scores (
    score_id INT PRIMARY KEY,
    user_id INT,
    anime_id INT,
    score TINYINT,
    comment TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (anime_id) REFERENCES Anime_Information(anime_id)
);

-- Table 4: Producers
CREATE TABLE Producers (
    producer_id INT PRIMARY KEY,
    producer_name TEXT NOT NULL
);

-- Table 5: Studios
CREATE TABLE Studios (
    studio_id INT PRIMARY KEY,
    studio_name VARCHAR(255) NOT NULL
);

CREATE TABLE licensors (
    licensor_id INT PRIMARY KEY,
    licensor_name VARCHAR(255) NOT NULL
);

-- Table 6: Anime Production
CREATE TABLE Anime_Production (
    production_id INT PRIMARY KEY,
    anime_id INT,
    producer_id INT,
    studio_id INT,
    licensor_id INT,
    FOREIGN KEY (anime_id) REFERENCES Anime_Information(anime_id),
    FOREIGN KEY (studio_id) REFERENCES Studios(studio_id),
    FOREIGN KEY (producer_id) REFERENCES Producers(producer_id),
    FOREIGN KEY (licensor_id) REFERENCES licensors(licensor_id)
);

-- Table 7: Anime Metadata
CREATE TABLE Anime_Metadata (
    metadata_id INT PRIMARY KEY,
    anime_id INT,
    episodes INT,
    aired VARCHAR(255),
    premiered VARCHAR(50),
    source VARCHAR(255),
    FOREIGN KEY (anime_id) REFERENCES Anime_Information(anime_id)
);

-- --- Table 8: Accounts
-- CREATE TABLE Accounts (
--     user_id INT AUTO_INCREMENT PRIMARY KEY,
--     username VARCHAR(255) NOT NULL UNIQUE,
--     password VARCHAR(255) NOT NULL
-- );

CREATE TABLE Review_Interactions (
    interaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    score_id INT NOT NULL,
    action ENUM('like', 'dislike') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (score_id) REFERENCES Anime_Scores(score_id) ON DELETE CASCADE,
    UNIQUE(user_id, score_id)
);

ALTER TABLE Review_Interactions
DROP FOREIGN KEY Review_Interactions_ibfk_2;

ALTER TABLE Review_Interactions
ADD CONSTRAINT Review_Interactions_ibfk_2
FOREIGN KEY (score_id)
REFERENCES Anime_Scores(score_id)
ON DELETE CASCADE;





-- ALTER TABLE Producers MODIFY producer_name VARCHAR(255) NULL;
-- ALTER TABLE Licensors MODIFY licensor_name VARCHAR(255) NULL;

-- after creating the tables, we can convert to auto increment
ALTER TABLE Anime_Scores
MODIFY COLUMN score_id INT AUTO_INCREMENT;


-- Merging the Users and Accounts table
ALTER TABLE Users MODIFY COLUMN user_id INT AUTO_INCREMENT;

ALTER TABLE Users
ADD COLUMN password VARCHAR(255) NOT NULL;

ALTER TABLE Users
ADD COLUMN role ENUM('user', 'admin') DEFAULT 'user';

ALTER TABLE Users
ADD CONSTRAINT unique_username UNIQUE (username);

DROP TABLE Accounts;

-- Adding likes and dislikes to Anime_Scores
ALTER TABLE Anime_Scores
ADD COLUMN likes INT DEFAULT 0,
ADD COLUMN dislikes INT DEFAULT 0;

