-- ========================================
-- Additional Tables for Nemo AI Assistant
-- ========================================
-- Run this script to add registrations and feedback tables
-- to your existing Supabase database

-- ========================================
-- 1. REGISTRATIONS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS public.registrations (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  event_id uuid NOT NULL,
  user_name text NOT NULL,
  user_email text NOT NULL,
  user_phone text NULL,
  status text NOT NULL DEFAULT 'confirmed'::text,
  registration_date timestamp with time zone NOT NULL DEFAULT now(),
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now(),
  
  CONSTRAINT registrations_pkey PRIMARY KEY (id),
  CONSTRAINT registrations_event_id_fkey FOREIGN KEY (event_id) 
    REFERENCES public.events(id) ON DELETE CASCADE,
  CONSTRAINT registrations_unique_user_event UNIQUE (event_id, user_email),
  CONSTRAINT registrations_status_check CHECK (
    status = ANY (ARRAY['confirmed'::text, 'cancelled'::text, 'waitlist'::text])
  )
) TABLESPACE pg_default;

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_registrations_event_id 
  ON public.registrations USING btree (event_id) TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_registrations_user_email 
  ON public.registrations USING btree (user_email) TABLESPACE pg_default;

-- Trigger to update updated_at timestamp
CREATE TRIGGER update_registrations_updated_at 
  BEFORE UPDATE ON public.registrations 
  FOR EACH ROW 
  EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- 2. FEEDBACK TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS public.feedback (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  event_id uuid NOT NULL,
  user_email text NOT NULL,
  rating integer NOT NULL,
  comments text NULL,
  submitted_at timestamp with time zone NOT NULL DEFAULT now(),
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  
  CONSTRAINT feedback_pkey PRIMARY KEY (id),
  CONSTRAINT feedback_event_id_fkey FOREIGN KEY (event_id) 
    REFERENCES public.events(id) ON DELETE CASCADE,
  CONSTRAINT feedback_rating_check CHECK (rating >= 1 AND rating <= 5),
  CONSTRAINT feedback_unique_user_event UNIQUE (event_id, user_email)
) TABLESPACE pg_default;

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_feedback_event_id 
  ON public.feedback USING btree (event_id) TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_feedback_rating 
  ON public.feedback USING btree (rating) TABLESPACE pg_default;

-- ========================================
-- 3. ROW LEVEL SECURITY (RLS) POLICIES
-- ========================================
-- Enable RLS
ALTER TABLE public.registrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback ENABLE ROW LEVEL SECURITY;

-- Allow anonymous users to read all registrations
CREATE POLICY "Allow anonymous read access" 
  ON public.registrations FOR SELECT 
  USING (true);

-- Allow anonymous users to insert registrations
CREATE POLICY "Allow anonymous insert access" 
  ON public.registrations FOR INSERT 
  WITH CHECK (true);

-- Allow anonymous users to read all feedback
CREATE POLICY "Allow anonymous read feedback" 
  ON public.feedback FOR SELECT 
  USING (true);

-- Allow anonymous users to insert feedback
CREATE POLICY "Allow anonymous insert feedback" 
  ON public.feedback FOR INSERT 
  WITH CHECK (true);

-- ========================================
-- 4. TRIGGER TO AUTO-INCREMENT PARTICIPANTS
-- ========================================
-- Automatically increment current_participants when someone registers
CREATE OR REPLACE FUNCTION increment_event_participants()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE public.events 
  SET current_participants = COALESCE(current_participants, 0) + 1
  WHERE id = NEW.event_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_registration_insert
  AFTER INSERT ON public.registrations
  FOR EACH ROW
  WHEN (NEW.status = 'confirmed')
  EXECUTE FUNCTION increment_event_participants();

-- Automatically decrement current_participants when registration is cancelled
CREATE OR REPLACE FUNCTION decrement_event_participants()
RETURNS TRIGGER AS $$
BEGIN
  IF OLD.status = 'confirmed' AND NEW.status = 'cancelled' THEN
    UPDATE public.events 
    SET current_participants = GREATEST(COALESCE(current_participants, 0) - 1, 0)
    WHERE id = OLD.event_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_registration_update
  AFTER UPDATE ON public.registrations
  FOR EACH ROW
  EXECUTE FUNCTION decrement_event_participants();

-- ========================================
-- VERIFICATION QUERIES
-- ========================================
-- Run these to verify tables were created:
-- SELECT * FROM public.registrations LIMIT 5;
-- SELECT * FROM public.feedback LIMIT 5;
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('registrations', 'feedback');
