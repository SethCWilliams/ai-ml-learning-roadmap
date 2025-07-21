-- Soccer Match Predictor Database Schema
-- Execute this SQL in your Supabase dashboard to create the database structure

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Leagues table - supports multiple soccer leagues
CREATE TABLE leagues (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE,
    country VARCHAR(50) NOT NULL,
    espn_code VARCHAR(20) NOT NULL UNIQUE,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Teams table - all teams across all leagues
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    abbreviation VARCHAR(10) NOT NULL,
    league_id INTEGER NOT NULL REFERENCES leagues(id),
    espn_id VARCHAR(20) NOT NULL,
    venue VARCHAR(200),
    city VARCHAR(100),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(espn_id, league_id)
);

-- Fixtures table - all matches
CREATE TABLE fixtures (
    id SERIAL PRIMARY KEY,
    espn_id VARCHAR(20) NOT NULL UNIQUE,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    league_id INTEGER NOT NULL REFERENCES leagues(id),
    home_team_id INTEGER NOT NULL REFERENCES teams(id),
    away_team_id INTEGER NOT NULL REFERENCES teams(id),
    home_score INTEGER,
    away_score INTEGER,
    status VARCHAR(50) NOT NULL,
    venue VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Team season statistics - cached from ESPN
CREATE TABLE team_season_stats (
    id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL REFERENCES teams(id),
    season VARCHAR(10) NOT NULL,
    league_id INTEGER NOT NULL REFERENCES leagues(id),
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    goals_for INTEGER DEFAULT 0,
    goals_against INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    games_played INTEGER GENERATED ALWAYS AS (wins + losses + draws) STORED,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(team_id, season, league_id)
);

-- Players table - for future player-level features
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    espn_id VARCHAR(20),
    team_id INTEGER NOT NULL REFERENCES teams(id),
    position VARCHAR(20),
    jersey_number INTEGER,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(espn_id, team_id)
);

-- Player season statistics - for advanced features
CREATE TABLE player_stats (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES players(id),
    season VARCHAR(10) NOT NULL,
    games INTEGER DEFAULT 0,
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    minutes INTEGER DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(player_id, season)
);

-- Predictions table - store all model predictions
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    fixture_id INTEGER NOT NULL REFERENCES fixtures(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    prob_home_win DECIMAL(5,3) NOT NULL CHECK (prob_home_win >= 0 AND prob_home_win <= 1),
    prob_draw DECIMAL(5,3) NOT NULL CHECK (prob_draw >= 0 AND prob_draw <= 1),
    prob_away_win DECIMAL(5,3) NOT NULL CHECK (prob_away_win >= 0 AND prob_away_win <= 1),
    predicted_outcome VARCHAR(10) NOT NULL CHECK (predicted_outcome IN ('Home Win', 'Draw', 'Away Win')),
    confidence DECIMAL(5,3) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    model_version VARCHAR(50) NOT NULL,
    features JSONB, -- Store feature vector for debugging
    CONSTRAINT check_probabilities_sum CHECK (ABS(prob_home_win + prob_draw + prob_away_win - 1.0) < 0.001)
);

-- API cache table - cache ESPN API responses
CREATE TABLE api_cache (
    id SERIAL PRIMARY KEY,
    endpoint_hash VARCHAR(64) NOT NULL UNIQUE,
    response_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Create indexes for performance
CREATE INDEX idx_teams_league_id ON teams(league_id);
CREATE INDEX idx_teams_espn_id ON teams(espn_id);
CREATE INDEX idx_fixtures_date ON fixtures(date);
CREATE INDEX idx_fixtures_league_id ON fixtures(league_id);
CREATE INDEX idx_fixtures_teams ON fixtures(home_team_id, away_team_id);
CREATE INDEX idx_fixtures_espn_id ON fixtures(espn_id);
CREATE INDEX idx_team_season_stats_team_season ON team_season_stats(team_id, season);
CREATE INDEX idx_players_team_id ON players(team_id);
CREATE INDEX idx_player_stats_player_season ON player_stats(player_id, season);
CREATE INDEX idx_predictions_fixture_id ON predictions(fixture_id);
CREATE INDEX idx_predictions_created_at ON predictions(created_at);
CREATE INDEX idx_api_cache_hash ON api_cache(endpoint_hash);
CREATE INDEX idx_api_cache_expires ON api_cache(expires_at);

-- Insert initial league data
INSERT INTO leagues (name, code, country, espn_code) VALUES 
    ('Premier League', 'EPL', 'England', 'eng.1'),
    ('Major League Soccer', 'MLS', 'United States', 'usa.1');

-- Create function to update timestamp columns automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to auto-update updated_at columns
CREATE TRIGGER update_leagues_updated_at BEFORE UPDATE ON leagues 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_fixtures_updated_at BEFORE UPDATE ON fixtures 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_players_updated_at BEFORE UPDATE ON players 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create a view for easy fixture queries with team names
CREATE VIEW fixture_details AS
SELECT 
    f.id,
    f.espn_id,
    f.date,
    l.name AS league_name,
    l.code AS league_code,
    ht.name AS home_team_name,
    ht.abbreviation AS home_team_abbr,
    at.name AS away_team_name,
    at.abbreviation AS away_team_abbr,
    f.home_score,
    f.away_score,
    f.status,
    f.venue
FROM fixtures f
JOIN leagues l ON f.league_id = l.id
JOIN teams ht ON f.home_team_id = ht.id
JOIN teams at ON f.away_team_id = at.id;

-- Grant necessary permissions (adjust as needed for your security model)
-- These are basic permissions - you may want to restrict further
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- Comments for documentation
COMMENT ON TABLE leagues IS 'Soccer leagues (Premier League, MLS, etc.)';
COMMENT ON TABLE teams IS 'All teams across all leagues';
COMMENT ON TABLE fixtures IS 'Match fixtures with results';
COMMENT ON TABLE team_season_stats IS 'Cached team season statistics from ESPN';
COMMENT ON TABLE players IS 'Player information for advanced features';
COMMENT ON TABLE player_stats IS 'Player season statistics';
COMMENT ON TABLE predictions IS 'ML model predictions with confidence scores';
COMMENT ON TABLE api_cache IS 'Cache for ESPN API responses to reduce API calls';
COMMENT ON VIEW fixture_details IS 'Easy-to-query view with team names for fixtures';