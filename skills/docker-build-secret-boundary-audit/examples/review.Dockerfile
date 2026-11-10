FROM alpine:3.20
ARG API_TOKEN
ENV DB_PASSWORD=example
RUN cat /run/secrets/missing
RUN echo "$API_TOKEN"
RUN --mount=type=secret,id=another cat /run/secrets/another
