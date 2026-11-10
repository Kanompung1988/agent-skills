FROM alpine:3.20
RUN --mount=type=secret,id=token,required=true cat /run/secrets/token >/dev/null
