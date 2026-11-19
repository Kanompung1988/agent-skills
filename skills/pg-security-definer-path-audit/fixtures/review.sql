CREATE FUNCTION public.unsafe_one() RETURNS integer
AS $$ SELECT 1; $$
LANGUAGE sql SECURITY DEFINER;
CREATE FUNCTION admin.needs_review() RETURNS integer
AS $$ SELECT 2; $$ LANGUAGE sql SECURITY DEFINER SET search_path = public;
