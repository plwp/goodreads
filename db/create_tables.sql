CREATE TABLE IF NOT EXISTS authors (
  id SERIAL PRIMARY KEY,
  author varchar(250) NOT NULL,
  average_rating REAL NOT NULL,
  rating_count INT NOT NULL
);

