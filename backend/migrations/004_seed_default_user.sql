-- Seed a default admin user and backfill existing data
-- Default password: admin123 (bcrypt hash)

INSERT INTO users (id, username, password_hash) VALUES
    (1, 'admin', '$2b$12$6gPYNY8q6TOdYPis/PDf.eGQkTrtaKBKbnRroShEBSBWGDhDkoS9q')
ON DUPLICATE KEY UPDATE username = username;

UPDATE todos SET user_id = 1 WHERE user_id IS NULL;
UPDATE chat_messages SET user_id = 1 WHERE user_id IS NULL;
