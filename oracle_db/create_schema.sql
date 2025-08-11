-- Create a new user/schema
CREATE USER chatbot_user IDENTIFIED BY "yourStrongPassword123";

-- Grant permissions
GRANT CONNECT, RESOURCE TO chatbot_user;

-- Optional: Set quotas (limits on storage)
-- ALTER USER chatbot_user QUOTA 100M ON USERS;

-- Optional: Allow password complexity enforcement (Oracle 12c+)
-- ALTER PROFILE DEFAULT LIMIT PASSWORD_VERIFY_FUNCTION verify_function;
