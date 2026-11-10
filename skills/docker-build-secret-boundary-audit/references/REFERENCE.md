BS001 sensitive-looking ARG name; BS002 ENV name; BS003 optional BuildKit secret mount; BS004 missing id and target in mount; BS005 file access without same-RUN mount; BS006 RUN uses credential-like ARG/ENV; BS007 secret mount env name conflicts with ARG/ENV.

Secret names are reported but values are never printed. Heuristics can produce false positives. BuildKit mounts are per-instruction and may specify custom target or env. The scanner does not evaluate an image build and cannot prove that secrets are absent from artifacts.
