-- Create a new user/schema
CREATE USER chatbot_user IDENTIFIED BY "yourStrongPassword123";

-- Grant permissions
GRANT CONNECT, RESOURCE TO chatbot_user;

GRANT CREATE SESSION TO CHATBOT_USER;