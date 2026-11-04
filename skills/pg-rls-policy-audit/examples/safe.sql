ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invoices FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON public.invoices
    TO app_user USING (tenant_id = current_setting('app.tenant_id')::uuid);
