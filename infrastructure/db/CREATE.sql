-- CREATE TABLE IF NOT EXISTS magazines (
-- 	magazin_idx VARCHAR(20) PRIMARY KEY,
-- 	name VARCHAR(100) NOT NULL,
-- 	publisher VARCHAR(100)
-- );

CREATE TABLE IF NOT EXISTS app_users (
	id SERIAL PRIMARY KEY,
	vk_user_id BIGINT NOT NULL UNIQUE,
	first_name VARCHAR(100),
	last_name VARCHAR(100),
	sex SMALLINT,
	birth_date DATE,
	age SMALLINT,
	city_id BIGINT,
	city_name VARCHAR(150),
	profile_url VARCHAR(255),
	created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS candidates (
	id SERIAL PRIMARY KEY,
	vk_candidate_id BIGINT NOT NULL UNIQUE,
	first_name VARCHAR(100),
	last_name VARCHAR(100),
	sex SMALLINT,
	birth_date DATE,
	age SMALLINT,
	city_id BIGINT,
	city_name VARCHAR(150),
	profile_url VARCHAR(255)NOT NULL,
	is_closed BOOLEAN NOT NULL DEFAULT FALSE,
	created_at TIMESTAMP NOT NULL DEFAULT NOW() 
);

CREATE TABLE IF NOT EXISTS candidate_photos (
	id SERIAL PRIMARY KEY,
	candidate_id INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
	vk_photo_id BIGINT NOT NULL,
	photo_url VARCHAR(255),
	likes_amount INTEGER NOT NULL DEFAULT 0,
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	UNIQUE(candidate_id, vk_photo_id)
);

CREATE TABLE IF NOT EXISTS favorites (
	id SERIAL PRIMARY KEY,
	app_user_id INTEGER NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
	candidate_id INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	UNIQUE(app_user_id, candidate_id)
);

CREATE TABLE IF NOT EXISTS blacklist (
	id SERIAL PRIMARY KEY,
	app_user_id INTEGER NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
	candidate_id INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	UNIQUE(app_user_id, candidate_id)
);

CREATE TABLE IF NOT EXISTS shown_candidates (
	id SERIAL PRIMARY KEY,
	app_user_id INTEGER NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
	candidate_id INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
	shown_at TIMESTAMP NOT NULL DEFAULT NOW(),
	UNIQUE(app_user_id, candidate_id)
);

CREATE TABLE IF NOT EXISTS search_sessions (
	id SERIAL PRIMARY KEY,
	app_user_id INTEGER NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	status VARCHAR(20) NOT NULL DEFAULT 'active'  
	-- finished cancelled
);

