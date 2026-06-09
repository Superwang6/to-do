-- Migration: Drop all foreign key constraints
-- The project no longer uses foreign keys; indexes are used for query acceleration instead.
-- Run against the todo_app database.

-- Drop self-referencing FK on todos.recurring_template_id
-- The idx_recurring_template index from migration 001 is retained
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

-- Drop fk_recurring_template from todos (explicitly named in migration 001)
CALL drop_fk_if_exists('todos', 'fk_recurring_template');

-- Drop auto-named FKs on message_todo (MySQL typically names these message_todo_ibfk_1, message_todo_ibfk_2)
CALL drop_fk_if_exists('message_todo', 'message_todo_ibfk_1');
CALL drop_fk_if_exists('message_todo', 'message_todo_ibfk_2');

DROP PROCEDURE IF EXISTS drop_fk_if_exists;
