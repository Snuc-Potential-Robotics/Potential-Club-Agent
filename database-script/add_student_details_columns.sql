-- ========================================
-- Add Student Details Columns to Registrations Table
-- ========================================
-- Run this SQL in Supabase SQL Editor to add student detail columns

-- Add new columns to registrations table
ALTER TABLE public.registrations 
ADD COLUMN IF NOT EXISTS user_class TEXT,
ADD COLUMN IF NOT EXISTS user_section TEXT,
ADD COLUMN IF NOT EXISTS user_year TEXT;

-- Add check constraints for valid values
ALTER TABLE public.registrations
DROP CONSTRAINT IF EXISTS user_class_check;

ALTER TABLE public.registrations
ADD CONSTRAINT user_class_check 
CHECK (user_class IS NULL OR user_class IN ('IoT', 'AIDS', 'Cyber'));

ALTER TABLE public.registrations
DROP CONSTRAINT IF EXISTS user_section_check;

ALTER TABLE public.registrations
ADD CONSTRAINT user_section_check 
CHECK (user_section IS NULL OR user_section IN ('A', 'B'));

ALTER TABLE public.registrations
DROP CONSTRAINT IF EXISTS user_year_check;

ALTER TABLE public.registrations
ADD CONSTRAINT user_year_check 
CHECK (user_year IS NULL OR user_year IN ('2023', '2024', '2025', '2026'));

-- Create index for faster queries by class
CREATE INDEX IF NOT EXISTS idx_registrations_user_class 
ON public.registrations(user_class) 
WHERE user_class IS NOT NULL;

-- Create index for faster queries by section  
CREATE INDEX IF NOT EXISTS idx_registrations_user_section 
ON public.registrations(user_section) 
WHERE user_section IS NOT NULL;

-- Create index for faster queries by year
CREATE INDEX IF NOT EXISTS idx_registrations_user_year 
ON public.registrations(user_year) 
WHERE user_year IS NOT NULL;

-- Verify columns were added
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'registrations'
AND column_name IN ('user_class', 'user_section', 'user_year');

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Student detail columns added successfully!';
    RAISE NOTICE '📊 New columns: user_class, user_section, user_year';
    RAISE NOTICE '🔍 Indexes created for better query performance';
    RAISE NOTICE '✓ Check constraints added for data validation';
END $$;
