CREATE USER aiohttp_security WITH PASSWORD 'aiohttp_security';
DROP DATABASE IF EXISTS aiohttp_security;
CREATE DATABASE aiohttp_security;
ALTER DATABASE aiohttp_security OWNER TO aiohttp_security;
GRANT ALL PRIVILEGES ON DATABASE aiohttp_security TO aiohttp_security;
