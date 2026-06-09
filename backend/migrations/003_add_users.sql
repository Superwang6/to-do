-- Create users table and add user_id to existing tables

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE INDEX ix_users_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE todos ADD COLUMN user_id INT NULL;
ALTER TABLE chat_messages ADD COLUMN user_id INT NULL;

CREATE INDEX ix_todos_user_id ON todos(user_id);
CREATE INDEX ix_chat_messages_user_id ON chat_messages(user_id);
