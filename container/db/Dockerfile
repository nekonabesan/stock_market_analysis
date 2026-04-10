FROM postgres:16-alpine

# Use scram-sha-256 authentication (requires cryptography package on client side)
ENV POSTGRES_INITDB_ARGS="--auth-host=scram-sha-256 --auth-local=scram-sha-256 --encoding=UTF-8 --locale=C"
