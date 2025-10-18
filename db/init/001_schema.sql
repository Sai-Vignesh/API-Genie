-- db/init/001_schema.sql
CREATE EXTENSION IF NOT EXISTS vector;

-- logical schemas
CREATE SCHEMA IF NOT EXISTS application_metadata;
CREATE SCHEMA IF NOT EXISTS api_catalog;

-- ===== application_metadata =====
CREATE TABLE IF NOT EXISTS application_metadata.user_account (
  user_id SERIAL PRIMARY KEY,
  name TEXT,
  email TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS application_metadata.database_schema (
  schema_id SERIAL PRIMARY KEY,
  version_number INT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS application_metadata.table_meta (
  table_id SERIAL PRIMARY KEY,
  schema_id INT NOT NULL REFERENCES application_metadata.database_schema(schema_id) ON DELETE CASCADE,
  table_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS application_metadata.column_meta (
  column_id SERIAL PRIMARY KEY,
  table_id INT NOT NULL REFERENCES application_metadata.table_meta(table_id) ON DELETE CASCADE,
  column_name TEXT NOT NULL,
  data_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS application_metadata.nl_query (
  query_id SERIAL PRIMARY KEY,
  user_id INT REFERENCES application_metadata.user_account(user_id),
  query_text TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS application_metadata.clarification (
  clarification_id SERIAL PRIMARY KEY,
  query_id INT NOT NULL REFERENCES application_metadata.nl_query(query_id) ON DELETE CASCADE,
  question_text TEXT NOT NULL,
  user_response_text TEXT
);

CREATE TABLE IF NOT EXISTS application_metadata.generated_sql (
  sql_id SERIAL PRIMARY KEY,
  query_id INT NOT NULL REFERENCES application_metadata.nl_query(query_id) ON DELETE CASCADE,
  sql_text TEXT NOT NULL,
  used_schema_version INT REFERENCES application_metadata.database_schema(schema_id),
  status TEXT CHECK (status IN ('pending','executed','error','needs_clarification')) DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS application_metadata.sql_execution_result (
  result_id SERIAL PRIMARY KEY,
  sql_id INT NOT NULL REFERENCES application_metadata.generated_sql(sql_id) ON DELETE CASCADE,
  success_flag BOOLEAN NOT NULL,
  error_message TEXT,
  output_summary TEXT
);

-- ===== api_catalog =====
CREATE TABLE IF NOT EXISTS api_catalog.category (
  category_id SERIAL PRIMARY KEY,
  category_name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS api_catalog.tag (
  tag_id SERIAL PRIMARY KEY,
  tag_name TEXT UNIQUE NOT NULL
);

-- main API table
CREATE TABLE IF NOT EXISTS api_catalog.api (
  api_id SERIAL PRIMARY KEY,
  api_name TEXT NOT NULL,
  description TEXT,
  base_url TEXT,
  auth_type TEXT,                -- e.g., 'apiKey', 'OAuth', 'None'
  https_supported BOOLEAN,
  cors_supported BOOLEAN,
  pricing_tier TEXT,             -- e.g., 'Free', 'Paid', 'Freemium'
  category_id INT REFERENCES api_catalog.category(category_id),
  -- optional embedding for recommendations
  description_embedding vector(1536)
);

-- many-to-many API <-> Tag
CREATE TABLE IF NOT EXISTS api_catalog.api_tag (
  api_id INT NOT NULL REFERENCES api_catalog.api(api_id) ON DELETE CASCADE,
  tag_id INT NOT NULL REFERENCES api_catalog.tag(tag_id) ON DELETE CASCADE,
  PRIMARY KEY (api_id, tag_id)
);

-- bootstrap a schema version row
INSERT INTO application_metadata.database_schema (version_number)
VALUES (1)
ON CONFLICT DO NOTHING;

-- Ensure uniqueness per category
CREATE UNIQUE INDEX IF NOT EXISTS api_api_name_category_id_uq
ON api_catalog.api (api_name, category_id);
