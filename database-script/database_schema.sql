-- Nemo AI Assistant Database Schema
-- Execute this SQL in Supabase SQL Editor

-- =============================================
-- TABLE: events
-- =============================================
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    location TEXT,
    total_slots INTEGER NOT NULL CHECK (total_slots > 0),
    available_slots INTEGER NOT NULL CHECK (available_slots >= 0),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT slots_check CHECK (available_slots <= total_slots)
);

-- Create index for date queries
CREATE INDEX IF NOT EXISTS idx_events_date ON events(date);
CREATE INDEX IF NOT EXISTS idx_events_active ON events(is_active);

-- =============================================
-- TABLE: registrations
-- =============================================
CREATE TABLE IF NOT EXISTS registrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    user_name TEXT NOT NULL,
    user_email TEXT NOT NULL,
    user_phone TEXT,
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status TEXT DEFAULT 'confirmed' CHECK (status IN ('confirmed', 'cancelled', 'waitlist')),
    CONSTRAINT unique_registration UNIQUE (event_id, user_email)
);

-- Create indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_registrations_email ON registrations(user_email);
CREATE INDEX IF NOT EXISTS idx_registrations_event ON registrations(event_id);
CREATE INDEX IF NOT EXISTS idx_registrations_status ON registrations(status);

-- =============================================
-- TABLE: feedback
-- =============================================
CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    user_email TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comments TEXT,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for event feedback queries
CREATE INDEX IF NOT EXISTS idx_feedback_event ON feedback(event_id);
CREATE INDEX IF NOT EXISTS idx_feedback_email ON feedback(user_email);

-- =============================================
-- FUNCTIONS
-- =============================================

-- Function to decrement available slots on registration
CREATE OR REPLACE FUNCTION decrement_available_slots()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'confirmed' THEN
        UPDATE events
        SET available_slots = available_slots - 1,
            updated_at = NOW()
        WHERE id = NEW.event_id
        AND available_slots > 0;
        
        IF NOT FOUND THEN
            RAISE EXCEPTION 'No available slots for this event';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to increment available slots on cancellation
CREATE OR REPLACE FUNCTION increment_available_slots()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status = 'confirmed' AND NEW.status = 'cancelled' THEN
        UPDATE events
        SET available_slots = available_slots + 1,
            updated_at = NOW()
        WHERE id = NEW.event_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- TRIGGERS
-- =============================================

-- Trigger to decrement slots on new registration
DROP TRIGGER IF EXISTS trg_decrement_slots ON registrations;
CREATE TRIGGER trg_decrement_slots
    BEFORE INSERT ON registrations
    FOR EACH ROW
    EXECUTE FUNCTION decrement_available_slots();

-- Trigger to increment slots on cancellation
DROP TRIGGER IF EXISTS trg_increment_slots ON registrations;
CREATE TRIGGER trg_increment_slots
    BEFORE UPDATE ON registrations
    FOR EACH ROW
    WHEN (OLD.status IS DISTINCT FROM NEW.status)
    EXECUTE FUNCTION increment_available_slots();

-- Trigger to update updated_at on events
DROP TRIGGER IF EXISTS trg_events_updated_at ON events;
CREATE TRIGGER trg_events_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- =============================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================

-- Enable RLS on all tables
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE registrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Events: Allow read for everyone
DROP POLICY IF EXISTS "Events are viewable by everyone" ON events;
CREATE POLICY "Events are viewable by everyone"
    ON events FOR SELECT
    USING (true);

-- Events: Allow insert/update for authenticated users (admin)
DROP POLICY IF EXISTS "Events are manageable by authenticated users" ON events;
CREATE POLICY "Events are manageable by authenticated users"
    ON events FOR ALL
    USING (auth.role() = 'authenticated');

-- Registrations: Allow insert for everyone (for AI agent)
DROP POLICY IF EXISTS "Anyone can create registrations" ON registrations;
CREATE POLICY "Anyone can create registrations"
    ON registrations FOR INSERT
    WITH CHECK (true);

-- Registrations: Allow read for everyone
DROP POLICY IF EXISTS "Registrations are viewable by everyone" ON registrations;
CREATE POLICY "Registrations are viewable by everyone"
    ON registrations FOR SELECT
    USING (true);

-- Registrations: Allow update for authenticated users
DROP POLICY IF EXISTS "Registrations are updatable by authenticated users" ON registrations;
CREATE POLICY "Registrations are updatable by authenticated users"
    ON registrations FOR UPDATE
    USING (auth.role() = 'authenticated');

-- Feedback: Allow insert for everyone
DROP POLICY IF EXISTS "Anyone can submit feedback" ON feedback;
CREATE POLICY "Anyone can submit feedback"
    ON feedback FOR INSERT
    WITH CHECK (true);

-- Feedback: Allow read for everyone
DROP POLICY IF EXISTS "Feedback is viewable by everyone" ON feedback;
CREATE POLICY "Feedback is viewable by everyone"
    ON feedback FOR SELECT
    USING (true);

-- =============================================
-- SAMPLE DATA
-- =============================================

-- Insert sample events
INSERT INTO events (name, description, date, location, total_slots, available_slots, is_active)
VALUES
    (
        'Robotics Workshop 2025',
        'Learn the fundamentals of robotics, including mechanics, electronics, and programming. Perfect for beginners!',
        '2025-10-15 14:00:00+00',
        'Engineering Lab A, Building 3',
        30,
        30,
        true
    ),
    (
        'Cybersecurity Basics',
        'Introduction to cybersecurity concepts, ethical hacking, and network security. Hands-on exercises included.',
        '2025-10-22 16:00:00+00',
        'Computer Lab B, Building 2',
        25,
        25,
        true
    ),
    (
        'AI & Machine Learning Seminar',
        'Explore the world of AI and ML with industry experts. Topics include neural networks, deep learning, and practical applications.',
        '2025-11-05 15:00:00+00',
        'Main Auditorium',
        50,
        50,
        true
    ),
    (
        'Web Development Bootcamp',
        'Full-stack web development bootcamp covering HTML, CSS, JavaScript, React, Node.js, and database integration.',
        '2025-11-12 13:00:00+00',
        'Computer Lab C, Building 2',
        20,
        20,
        true
    ),
    (
        'Electronics Project Exhibition',
        'Showcase your electronics projects and see what others have built. Open to all skill levels.',
        '2025-11-20 10:00:00+00',
        'Exhibition Hall, Building 1',
        100,
        100,
        true
    )
ON CONFLICT (id) DO NOTHING;

-- =============================================
-- UTILITY VIEWS
-- =============================================

-- View for upcoming events with registration stats
CREATE OR REPLACE VIEW v_upcoming_events AS
SELECT 
    e.id,
    e.name,
    e.description,
    e.date,
    e.location,
    e.total_slots,
    e.available_slots,
    e.total_slots - e.available_slots as registered_count,
    CASE 
        WHEN e.available_slots = 0 THEN true 
        ELSE false 
    END as is_full,
    e.is_active,
    COUNT(DISTINCT r.id) as confirmed_registrations,
    ROUND(AVG(f.rating), 2) as average_rating,
    COUNT(DISTINCT f.id) as feedback_count
FROM events e
LEFT JOIN registrations r ON e.id = r.event_id AND r.status = 'confirmed'
LEFT JOIN feedback f ON e.id = f.event_id
WHERE e.date >= NOW()
AND e.is_active = true
GROUP BY e.id, e.name, e.description, e.date, e.location, e.total_slots, e.available_slots, e.is_active
ORDER BY e.date ASC;

-- =============================================
-- SUCCESS MESSAGE
-- =============================================
DO $$
BEGIN
    RAISE NOTICE '✅ Database schema created successfully!';
    RAISE NOTICE '📊 Tables: events, registrations, feedback';
    RAISE NOTICE '🔧 Functions and triggers configured';
    RAISE NOTICE '🔒 Row Level Security enabled';
    RAISE NOTICE '📝 Sample data inserted';
    RAISE NOTICE '👉 You can now start the backend server';
END $$;
