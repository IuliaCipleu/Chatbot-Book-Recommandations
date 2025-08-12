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

CREATE TABLE user_history (
    history_id    NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id       NUMBER REFERENCES users(user_id) ON DELETE CASCADE,
    query_text    VARCHAR2(1000),
    recommended_title VARCHAR2(255),
    summary       CLOB,
    image_url     VARCHAR2(1000),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

