-- Extend users table
ALTER TABLE users
ADD COLUMN email VARCHAR(255) UNIQUE,
ADD COLUMN avatar VARCHAR(255),
ADD COLUMN updated_at DATETIME DEFAULT NOW() ON UPDATE NOW();

-- Create user_settings table
CREATE TABLE user_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    key VARCHAR(64) NOT NULL,
    value TEXT NOT NULL,
    created_at DATETIME DEFAULT NOW(),
    updated_at DATETIME DEFAULT NOW() ON UPDATE NOW(),
    UNIQUE KEY user_key_unique (user_id, key)
);

-- Create index for user_settings
CREATE INDEX idx_user_settings_user_id ON user_settings(user_id);