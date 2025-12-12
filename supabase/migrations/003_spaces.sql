-- Spaces (workspaces) for multi-tenancy
-- Each user can have multiple spaces, each containing their own documents and chat history

CREATE TABLE IF NOT EXISTS spaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Space metadata
    name TEXT NOT NULL,
    description TEXT,
    cover_image_url TEXT,
    
    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'processing', 'archived')),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE spaces ENABLE ROW LEVEL SECURITY;

-- Users can only access their own spaces
CREATE POLICY "Users can view own spaces"
    ON spaces FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own spaces"
    ON spaces FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own spaces"
    ON spaces FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own spaces"
    ON spaces FOR DELETE
    USING (auth.uid() = user_id);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_spaces_user_id ON spaces(user_id);
CREATE INDEX IF NOT EXISTS idx_spaces_created_at ON spaces(created_at DESC);

-- Trigger to automatically update updated_at
CREATE TRIGGER spaces_updated_at
    BEFORE UPDATE ON spaces
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
