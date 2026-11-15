-- BugDiag PostgreSQL + pgvector Initialization Script
-- Enables vector extension and configures initial schema settings

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'BugDiag PostgreSQL extensions (vector, uuid-ossp) initialized successfully.';
END $$;
