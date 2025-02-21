-- Create players table
CREATE TABLE IF NOT EXISTS players (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    level VARCHAR(50) CHECK (level IN ('Beginner', 'Intermediate', 'Advanced', 'Professional')),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create tournaments table
CREATE TABLE IF NOT EXISTS tournaments (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    location VARCHAR(255) NOT NULL,
    type VARCHAR(50) CHECK (type IN ('Singles', 'Doubles', 'Mixed')),
    level VARCHAR(50) CHECK (level IN ('Local', 'Regional', 'National', 'International')),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create tournament_registrations table
CREATE TABLE IF NOT EXISTS tournament_registrations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    tournament_id UUID REFERENCES tournaments(id) ON DELETE CASCADE,
    player_id UUID REFERENCES players(id) ON DELETE CASCADE,
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tournament_id, player_id)
);

-- Create training_plans table
CREATE TABLE IF NOT EXISTS training_plans (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    player_id UUID REFERENCES players(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    focus_area VARCHAR(50) CHECK (focus_area IN ('Technique', 'Fitness', 'Strategy', 'Mental Game', 'Match Practice')),
    intensity INTEGER CHECK (intensity BETWEEN 1 AND 5),
    technical_goal TEXT,
    fitness_goal TEXT,
    tactical_goal TEXT,
    schedule JSONB,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create group_training_sessions table
CREATE TABLE IF NOT EXISTS group_training_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    date DATE NOT NULL,
    time TIME NOT NULL,
    level VARCHAR(50) CHECK (level IN ('Beginner', 'Intermediate', 'Advanced', 'Professional')),
    max_participants INTEGER,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create group_training_attendance table
CREATE TABLE IF NOT EXISTS group_training_attendance (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES group_training_sessions(id) ON DELETE CASCADE,
    player_id UUID REFERENCES players(id) ON DELETE CASCADE,
    attendance_status VARCHAR(20) CHECK (attendance_status IN ('Present', 'Absent', 'Late')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, player_id)
);

-- Create training_reports table
CREATE TABLE IF NOT EXISTS training_reports (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    training_type VARCHAR(20) CHECK (training_type IN ('Group', 'Individual')),
    session_id UUID,
    training_plan_id UUID,
    report_date DATE NOT NULL,
    performance_rating INTEGER CHECK (performance_rating BETWEEN 1 AND 5),
    attendance TEXT[],
    achievements TEXT,
    areas_for_improvement TEXT,
    coach_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT training_reference CHECK (
        (training_type = 'Group' AND session_id IS NOT NULL AND training_plan_id IS NULL) OR
        (training_type = 'Individual' AND training_plan_id IS NOT NULL AND session_id IS NULL)
    ),
    FOREIGN KEY (session_id) REFERENCES group_training_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (training_plan_id) REFERENCES training_plans(id) ON DELETE CASCADE
);

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";