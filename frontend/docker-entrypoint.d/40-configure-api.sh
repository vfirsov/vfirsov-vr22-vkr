#!/bin/sh
set -eu

# Configure the API at container startup so one frontend image can be used
# in Local, Demo and Prod. API_UPSTREAM is an origin, without a path.
snippet=/etc/nginx/snippets/api.conf
upstream=${API_UPSTREAM:-}

if [ -z "$upstream" ]; then
    cat > "$snippet" <<'NGINX'
default_type application/json;
add_header Cache-Control "no-store" always;
add_header X-Content-Type-Options nosniff always;
return 503 '{"error":"API is not configured"}';
NGINX
    exit 0
fi

# Only an HTTP(S) origin is allowed. This excludes credentials, paths,
# query strings, whitespace and Nginx directives from the generated file.
case "$upstream" in
    *[!A-Za-z0-9.:/-]*)
        printf '%s\n' 'API_UPSTREAM contains characters that are not allowed in an HTTP(S) origin.' >&2
        exit 1
        ;;
esac
if ! printf '%s\n' "$upstream" | grep -Eq '^https?://[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?(:[0-9]{1,5})?/?$'; then
    printf '%s\n' 'API_UPSTREAM must be an http(s) origin, e.g. http://backend:8000, without credentials or a path.' >&2
    exit 1
fi

upstream=${upstream%/}
authority=${upstream#*://}
case "$authority" in
    *:*)
        port=${authority##*:}
        if [ "$port" -lt 1 ] || [ "$port" -gt 65535 ]; then
            printf '%s\n' 'API_UPSTREAM port must be between 1 and 65535.' >&2
            exit 1
        fi
        ;;
esac

# No URI suffix in proxy_pass: /api and /api/... reach the backend unchanged.
cat > "$snippet" <<NGINX
proxy_pass "$upstream";
proxy_http_version 1.1;
proxy_set_header Host \$proxy_host;
proxy_set_header X-Real-IP \$remote_addr;
proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto \$forwarded_proto;
proxy_connect_timeout 5s;
proxy_read_timeout 30s;
proxy_ssl_server_name on;
proxy_ssl_verify on;
proxy_ssl_trusted_certificate /etc/ssl/certs/ca-certificates.crt;
NGINX

