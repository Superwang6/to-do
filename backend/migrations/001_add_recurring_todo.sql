-- Migration: Add recurring todo support
-- Run against the todos database

ALTER TABLE todos
    ADD COLUMN type ENUM('once', 'recurring') NOT NULL DEFAULT 'once' AFTER status,
    ADD COLUMN recurrence_rule JSON NULL AFTER type,
    ADD COLUMN recurring_template_id INT NULL AFTER recurrence_rule,
    ADD INDEX idx_recurring_template (recurring_template_id),
    ADD CONSTRAINT fk_recurring_template
        FOREIGN KEY (recurring_template_id) REFERENCES todos(id)
        ON DELETE SET NULL;
