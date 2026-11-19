CREATE OR REPLACE FUNCTION admin.check_job()
RETURNS boolean
LANGUAGE sql
SECURITY DEFINER
SET search_path = admin, pg_temp
AS $$ SELECT true; $$;
