CREATE DATABASE anime_db;
USE anime_db;


-- Table 2: Anime Information 
CREATE TABLE Anime_Information (
    anime_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    english_name VARCHAR(255),
    other_name VARCHAR(255),
    synopsis TEXT,
    type VARCHAR(50)
);

-- Table 3: Anime Scores
CREATE TABLE Anime_Scores (
    score_id INT PRIMARY KEY AUTO_INCREMENT,
    anime_id INT,
    score FLOAT,
    ranking INT,
    popularity INT,
    FOREIGN KEY (anime_id) REFERENCES Anime_Information(anime_id)
);


