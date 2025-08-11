import oracledb
from auth.encrypt import hash_password  # make sure this uses bcrypt
from auth.encrypt import verify_password

def insert_user(
    conn_string: str,
    db_user: str,
    db_password: str,
    username: str,
    email: str,
    plain_password: str,
    language: str = "english",
    profile: str = "adult",
    voice_enabled: bool = False
) -> None:
    """
    Inserts a new user into the Oracle users table with a securely hashed password.
    
    Args:
        conn_string (str): Oracle DSN, e.g. "host:port/service"
        db_user (str): Oracle username with insert access
        db_password (str): Oracle password
        username (str): New user's username
        email (str): Email address
        plain_password (str): Raw password to hash before storing
        language (str): User's preferred language
        profile (str): Reader profile (child/teen/adult/technical)
        voice_enabled (bool): Whether the user prefers voice input
    """
    try:
        conn = oracledb.connect(user=db_user, password=db_password, dsn=conn_string)
        cur = conn.cursor()

        password_hash = hash_password(plain_password)
        voice_flag = 'Y' if voice_enabled else 'N'

        cur.execute("""
            INSERT INTO users (username, email, password_hash, language, profile, voice_enabled)
            VALUES (:1, :2, :3, :4, :5, :6)
        """, (username, email, password_hash, language, profile, voice_flag))

        conn.commit()
        print(f"User '{username}' inserted successfully.")
    
    except Exception as e:
        print(f"Failed to insert user: {e}")
    
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
            
def get_user(conn_string, db_user, db_password, username):
    """Retrieve a user by username."""
    try:
        conn = oracledb.connect(user=db_user, password=db_password, dsn=conn_string)
        cur = conn.cursor()
        cur.execute("SELECT username, email, language, profile, voice_enabled FROM users WHERE username = :1", (username,))
        row = cur.fetchone()
        if row:
            return {
                "username": row[0],
                "email": row[1],
                "language": row[2],
                "profile": row[3],
                "voice_enabled": row[4] == 'Y'
            }
        return None
    except Exception as e:
        print(f"Failed to get user: {e}")
        return None
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

def update_user(conn_string, db_user, db_password, username, **kwargs):
    """Update user fields. kwargs can include email, language, profile, voice_enabled, plain_password."""
    try:
        conn = oracledb.connect(user=db_user, password=db_password, dsn=conn_string)
        cur = conn.cursor()
        fields = []
        values = []
        if 'email' in kwargs:
            fields.append('email = :email')
            values.append(kwargs['email'])
        if 'language' in kwargs:
            fields.append('language = :language')
            values.append(kwargs['language'])
        if 'profile' in kwargs:
            fields.append('profile = :profile')
            values.append(kwargs['profile'])
        if 'voice_enabled' in kwargs:
            fields.append('voice_enabled = :voice_enabled')
            values.append('Y' if kwargs['voice_enabled'] else 'N')
        if 'plain_password' in kwargs:
            from auth.encrypt import hash_password
            fields.append('password_hash = :password_hash')
            values.append(hash_password(kwargs['plain_password']))
        if not fields:
            print("No fields to update.")
            return
        values.append(username)
        sql = f"UPDATE users SET {', '.join(fields)} WHERE username = :{len(values)}"
        cur.execute(sql, values)
        conn.commit()
        print(f"User '{username}' updated successfully.")
    except Exception as e:
        print(f"Failed to update user: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

def delete_user(conn_string, db_user, db_password, username):
    """Delete a user by username."""
    try:
        conn = oracledb.connect(user=db_user, password=db_password, dsn=conn_string)
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE username = :1", (username,))
        conn.commit()
        print(f"User '{username}' deleted successfully.")
    except Exception as e:
        print(f"Failed to delete user: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

def login_user(conn_string, db_user, db_password, username, plain_password):
    """Authenticate user by username and password. Returns user dict if valid, else None."""
    try:
        conn = oracledb.connect(user=db_user, password=db_password, dsn=conn_string)
        cur = conn.cursor()
        cur.execute("SELECT password_hash, email, language, profile, voice_enabled FROM users WHERE username = :1", (username,))
        row = cur.fetchone()
        if not row:
            print("User not found.")
            return None
        
        if verify_password(plain_password, row[0]):
            return {
                "username": username,
                "email": row[1],
                "language": row[2],
                "profile": row[3],
                "voice_enabled": row[4] == 'Y'
            }
        else:
            print("Invalid password.")
            return None
    except Exception as e:
        print(f"Login failed: {e}")
        return None
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()
