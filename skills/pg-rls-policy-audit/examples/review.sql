ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;
CREATE POLICY open_policy ON public.invoices TO PUBLIC USING (true) WITH CHECK (true);
