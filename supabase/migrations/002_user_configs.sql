-- Per-user configuration for API keys and preferences
-- API keys are stored encrypted at rest by Supabase

CREATE TABLE IF NOT EXISTS user_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- API Keys (stored encrypted at rest)
    openai_api_key TEXT,
    llama_cloud_api_key TEXT,
    cohere_api_key TEXT,
    
    -- Infrastructure
    qdrant_url TEXT,  -- User's Qdrant instance URL
    
    -- Preferences
    default_llm_model TEXT DEFAULT 'gpt-4o',
    theme TEXT DEFAULT 'system' CHECK (theme IN ('light', 'dark', 'system')),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Each user can only have one config
    UNIQUE(user_id)
);

-- Enable Row Level Security
ALTER TABLE user_configs ENABLE ROW LEVEL SECURITY;

-- Users can only access their own config
CREATE POLICY "Users can view own config"
    ON user_configs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own config"
    ON user_configs FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own config"
    ON user_configs FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own config"
    ON user_configs FOR DELETE
    USING (auth.uid() = user_id);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_configs_user_id ON user_configs(user_id);

-- Trigger to automatically update updated_at
CREATE TRIGGER user_configs_updated_at
    BEFORE UPDATE ON user_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
