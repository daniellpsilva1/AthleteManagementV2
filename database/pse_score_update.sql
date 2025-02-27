-- Alter PSE scores table if it doesn't exist
CREATE TABLE IF NOT EXISTS player_pse_scores (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    player_id UUID REFERENCES players(id),
    report_id UUID REFERENCES training_reports(id),
    pse_score INTEGER CHECK (pse_score BETWEEN 1 AND 10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add trigger to update updated_at timestamp if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_player_pse_scores_updated_at ON player_pse_scores;
CREATE TRIGGER update_player_pse_scores_updated_at
    BEFORE UPDATE ON player_pse_scores
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();