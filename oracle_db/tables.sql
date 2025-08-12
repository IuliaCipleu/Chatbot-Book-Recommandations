-- Drop tables if they exist (order matters due to FKs)
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE user_read_books CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE user_history CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE books CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE users CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/

-- Users table
CREATE TABLE users (
        user_id       NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        username      VARCHAR2(100) UNIQUE NOT NULL,
        email         VARCHAR2(255),
        password_hash VARCHAR2(255) NOT NULL,
        language      VARCHAR2(20),
        profile       VARCHAR2(20),
        voice_enabled CHAR(1) DEFAULT 'N' CHECK (voice_enabled IN ('Y', 'N')),
        created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Books table
CREATE TABLE books (
        book_id   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        title     VARCHAR2(512) NOT NULL,
        author    VARCHAR2(255),
        -- add more metadata fields as needed
        UNIQUE (title)
);

-- User read books (link table)
CREATE TABLE user_read_books (
        user_id   NUMBER REFERENCES users(user_id) ON DELETE CASCADE,
        book_id   NUMBER REFERENCES books(book_id) ON DELETE CASCADE,
        read_date DATE DEFAULT SYSDATE,
        rating    NUMBER, -- optional
        PRIMARY KEY (user_id, book_id)
);

-- User history
CREATE TABLE user_history (
        history_id    NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        user_id       NUMBER REFERENCES users(user_id) ON DELETE CASCADE,
        book_id       NUMBER REFERENCES books(book_id),
        query_text    VARCHAR2(1000),
        recommended_title VARCHAR2(255),
        summary       CLOB,
        image_url     VARCHAR2(1000),
        created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);