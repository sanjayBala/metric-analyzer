-- SEED SQL
CREATE TABLE IF NOT EXISTS metric_deployment (
    repository_name CHAR(120) NOT NULL,
    pipeline_id INTEGER NOT NULL,
    pipeline_timestamp TIMESTAMP NOT NULL,
    pipeline_status BOOLEAN NOT NULL,
    PRIMARY KEY(pipeline_id, pipeline_timestamp)
);