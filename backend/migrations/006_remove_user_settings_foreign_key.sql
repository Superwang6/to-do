-- Migration: Remove foreign key constraint from user_settings table
-- The project no longer uses foreign keys; indexes are used for query acceleration instead.
-- Run against the todo_app database.

-- Drop foreign key constraint from user_settings table
DROP PROCEDURE IF EXISTS drop_fk_if_exists;

DELIMITER //
CREATE PROCEDURE drop_fk_if_exists(IN tbl VARCHAR(64), IN fk_name VARCHAR(64))
BEGIN
    DECLARE cnt INT DEFAULT 0;
    SELECT COUNT(*) INTO cnt
        FROM information_schema.TABLE_CONSTRAINTS
        WHERE CONSTRAINT_TYPE = 'FOREIGN KEY'
          AND TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = tbl
          AND CONSTRAINT_NAME = fk_name;
    IF cnt > 0 THEN
        SET @stmt = CONCAT('ALTER TABLE ', tbl, ' DROP FOREIGN KEY ', fk_name);
        PREPARE stmt FROM @stmt;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END //
DELIMITER ;

-- Drop foreign key from user_settings (MySQL typically names these user_settings_ibfk_1)
CALL drop_fk_if_exists('user_settings', 'user_settings_ibfk_1');

DROP PROCEDURE IF EXISTS drop_fk_if_exists;