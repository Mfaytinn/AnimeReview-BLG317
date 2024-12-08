USE anime_db;

-- Disable safe updates for bulk delete
SET SQL_SAFE_UPDATES = 0;

-- Delete all data from existing tables
DELETE FROM Anime_Production;
DELETE FROM Studios;
DELETE FROM Producers;
DELETE FROM licensors;
DELETE FROM Anime_Scores;
DELETE FROM Users;
DELETE FROM Anime_Metadata;
DELETE FROM Anime_Information;

-- Insert sample data into Users first (with valid user_ids)
INSERT INTO Users (user_id, username, gender, birthday, place, joined, days_watched) VALUES
(1, 'AnimeFan1', 'Male', '1990-01-15', 'Tokyo', '2024-01-01', 150.5),
(2, 'AnimeFan2', 'Female', NULL, 'Osaka', '2024-05-15', 75.0),  -- NULL birthday
(3, 'AnimeFan3', NULL, '1995-07-30', 'Kyoto', '2024-07-12', NULL);  -- NULL gender and days_watched

-- Insert sample data into Studios
INSERT INTO Studios (studio_id, studio_name) VALUES
(1, 'Madhouse'),
(2, 'Studio Ghibli'),
(3, 'Bones'),
(4, 'MAPPA'),
(5, 'Toei Animation');

-- Insert sample data into Anime_Information (with null values for testing)
INSERT INTO Anime_Information (anime_id, anime_name, english_name, other_name, synopsis, type_anime, genres) VALUES
(1, 'One Punch Man', 'One Punch Man', 'ワンパンマン', 'Saitama is a superhero who can defeat any opponent with a single punch, but his overwhelming power has left him bored and searching for an opponent who can challenge him.', 'TV', 'Action, Comedy, Superhero'),
(2, 'Spirited Away', 'Spirited Away', '千と千尋の神隠し', 'A young girl becomes trapped in a mysterious and magical world and must find a way to rescue her parents and return home.', 'Movie', 'Fantasy, Adventure'),
(3, 'Fullmetal Alchemist: Brotherhood', NULL, '鋼の錬金術師', 'Two brothers use alchemy in search of the Philosopher\'s Stone to restore their bodies after a failed alchemy experiment.', 'TV', 'Action, Adventure, Fantasy'),  -- NULL English name
(4, 'Attack on Titan', NULL, NULL, 'In a world where humanity lives in walled cities to protect themselves from giant humanoid creatures known as Titans, a young soldier fights to protect his home.', NULL, NULL);  -- NULL English name and other name

-- Insert sample data into Producers (with null values for testing)
INSERT INTO Producers (producer_id, producer_name) VALUES
(1, 'J.C. Staff'),
(2, 'Studio Ghibli'),
(3, NULL),  -- NULL producer name
(4, 'MAPPA');

-- Insert sample data into licensors (with null values for testing)
INSERT INTO licensors (licensor_id, licensor_name) VALUES
(1, 'Funimation'),
(2, 'Netflix'),
(3, NULL),  -- NULL licensor name
(4, 'Hulu');

-- Insert sample data into Anime_Production (with null values for testing)
INSERT INTO Anime_Production (production_id, anime_id, producer_id, studio_id, licensor_id) VALUES
(1, 1, 1, 1, 1),
(2, 2, NULL, 2, 2),  -- NULL producer_id
(3, 3, 3, NULL, 3),  -- NULL studio_id
(4, 4, 4, 4, NULL);  -- NULL licensor_id

-- Insert sample data into Anime_Metadata (with null values for testing)
INSERT INTO Anime_Metadata (metadata_id, anime_id, episodes, aired, premiered, source) VALUES
(1, 1, 12, '2015-10-05', '2015-10-05', 'Manga'),
(2, 2, 1, '2001-07-20', NULL, NULL),  -- NULL aired and premiered
(3, 3, NULL, '2009-04-05', '2009-04-05', 'Manga'),  -- NULL episodes
(4, 4, 25, NULL, NULL, 'Manga');  -- NULL aired and premiered

-- Insert sample data into Anime_Scores (now that users exist)
INSERT INTO Anime_Scores (score_id, user_id, anime_id, score, comment) VALUES
(1, 1, 1, 9, 'Amazing action sequences!'),
(2, 1, 2, NULL, 'A masterpiece of animation.'),  -- NULL score
(4, 1, 4, 7, NULL);  -- NULL comment
