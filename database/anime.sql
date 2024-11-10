USE anime_db;


-- Table 1: Users
CREATE TABLE Users (
    user_id INT PRIMARY KEY,
    username VARCHAR(50) NOT NULL
);

-- Table 2: Anime Information 
CREATE TABLE Anime_Information (
    anime_id INT PRIMARY KEY,
    anime_name VARCHAR(255) NOT NULL,
    english_name VARCHAR(255),
    other_name VARCHAR(255),
    synopsis TEXT,
    type_anime VARCHAR(50)
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

-- Table 4: Producers
CREATE TABLE Producers (
    producer_id INT PRIMARY KEY AUTO_INCREMENT,
    producer_name VARCHAR(255) NOT NULL
);

-- Table 5: Studios
CREATE TABLE Studios (
    studio_id INT PRIMARY KEY AUTO_INCREMENT,
    studio_name VARCHAR(255) NOT NULL
);

-- Table 6: Anime Production
CREATE TABLE Anime_Production (
    production_id INT PRIMARY KEY AUTO_INCREMENT,
    anime_id INT,
    producer_id INT,
    studio_id INT,
    licensors VARCHAR(255),
    FOREIGN KEY (anime_id) REFERENCES Anime_Information(anime_id),
    FOREIGN KEY (producer_id) REFERENCES Producers(producer_id),
    FOREIGN KEY (studio_id) REFERENCES Studios(studio_id)
);

-- Table 7: Anime Metadata
CREATE TABLE Anime_Metadata (
    metadata_id INT PRIMARY KEY AUTO_INCREMENT,
    anime_id INT,
    episodes INT,
    aired VARCHAR(255),
    premiered VARCHAR(50),
    source VARCHAR(255),
    FOREIGN KEY (anime_id) REFERENCES Anime_Information(anime_id)
);

-- Table 8: Anime Genres
CREATE TABLE Anime_Genres (
    anime_id INT,
    genres VARCHAR(255),
    FOREIGN KEY (anime_id) REFERENCES Anime_Information(anime_id)
);

-- Table 9: User Ratings
CREATE TABLE User_Ratings (
    user_id INT,
    anime_id INT,
    anime_title VARCHAR(255),
    rating FLOAT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (anime_id) REFERENCES Anime_Information(anime_id)
);
