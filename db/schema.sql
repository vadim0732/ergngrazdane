PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    login         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    full_name     TEXT    NOT NULL,
    phone         TEXT    NOT NULL,
    email         TEXT    NOT NULL,
    role          TEXT    NOT NULL DEFAULT 'user'
                  CHECK (role IN ('user', 'admin'))
);

CREATE TABLE services (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT NOT NULL UNIQUE
);

CREATE TABLE applications (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    service_id     INTEGER NOT NULL,
    receive_date   TEXT    NOT NULL,          -- ДД.ММ.ГГГГ
    payment        TEXT    NOT NULL
                   CHECK (payment IN ('Наличные', 'Перевод')),
    status         TEXT    NOT NULL DEFAULT 'Новая'
                   CHECK (status IN ('Новая', 'В обработке', 'Услуга оказана')),
    review         TEXT,
    created_at     TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE RESTRICT
);

INSERT INTO services (name) VALUES
    ('Выписка об основных характеристиках объекта'),
    ('Выписка о переходе прав'),
    ('Выписка о кадастровой стоимости');