CREATE TABLE IF NOT EXISTS images_table (
    hash_id VARCHAR PRIMARY KEY,
    url VARCHAR,
    emotion_angry NUMERIC,
    emotion_sad NUMERIC,
    emotion_happy NUMERIC,
    emotion_fear NUMERIC,
    emotion_neutral NUMERIC,
    emotion_surprise NUMERIC
);