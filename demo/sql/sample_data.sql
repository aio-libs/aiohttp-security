-- create users table
CREATE TABLE IF NOT EXISTS users
(
  id integer NOT NULL,
  login character varying(256) NOT NULL,
  passwd character varying(256) NOT NULL,
  is_superuser boolean NOT NULL DEFAULT false,
  disabled boolean NOT NULL DEFAULT false,
  CONSTRAINT user_pkey PRIMARY KEY (id),
  CONSTRAINT user_login_key UNIQUE (login)
);

-- and permissions for them
CREATE TABLE IF NOT EXISTS permissions
(
  id integer NOT NULL,
  user_id integer NOT NULL,
  perm_name character varying(64) NOT NULL,
  CONSTRAINT permission_pkey PRIMARY KEY (id),
  CONSTRAINT user_permission_fkey FOREIGN KEY (user_id)
      REFERENCES users (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE
);

-- insert some data
INSERT INTO users(id, login, passwd, is_superuser, disabled)
VALUES (1, 'admin', 'admin_pass', TRUE, FALSE);
INSERT INTO users(id, login, passwd, is_superuser, disabled)
VALUES (2, 'moderator', 'moderator_pass', FALSE, FALSE);
INSERT INTO users(id, login, passwd, is_superuser, disabled)
VALUES (3, 'user', 'user_pass', FALSE, FALSE);

INSERT INTO permissions(id, user_id, perm_name)
VALUES (1, 2, 'protected');
INSERT INTO permissions(id, user_id, perm_name)
VALUES (2, 2, 'public');
INSERT INTO permissions(id, user_id, perm_name)
VALUES (3, 3, 'public');
