"""
Unit tests for the sync_chromadb_to_oracle utility.
These tests verify the synchronization logic between ChromaDB and an Oracle database,
ensuring that book titles are correctly inserted or skipped based on their existence
in the database. The tests cover scenarios including inserting new titles, skipping
existing titles, and handling missing or malformed metadata.
Mocks are used for environment variables, ChromaDB client, Oracle database connection,
and dotenv loading to isolate and control test behavior.
"""
from unittest.mock import patch, MagicMock
import sys
import importlib

@patch("chromadb.PersistentClient")
@patch("oracledb.connect")
@patch("dotenv.load_dotenv")
@patch("os.environ.get")
def test_sync_inserts_new_titles(mock_env_get, mock_load_dotenv, mock_oracle_connect, mock_chroma_client):
    """
    Tests that new book titles from ChromaDB are correctly inserted into the Oracle database.
    This test mocks environment variables, ChromaDB collection, and Oracle database connection.
    It simulates a scenario where the database does not contain any of the books present in ChromaDB.
    The test verifies that for each book title retrieved from ChromaDB:
        - A SELECT query is executed to check for existence in the database.
        - An INSERT query is executed if the book does not exist.
        - The database commit is called for each inserted book.
    Args:
        mock_env_get: Mock for environment variable retrieval.
        mock_load_dotenv: Mock for dotenv loading.
        mock_oracle_connect: Mock for Oracle database connection.
        mock_chroma_client: Mock for ChromaDB client.
    """
    
    # Setup environment variables
    mock_env_get.side_effect = lambda k: {
        "DB_CONN_STRING": "fake_dsn",
        "DB_USER": "user",
        "DB_PASSWORD": "pass"
    }[k]

    # Mock ChromaDB collection
    mock_collection = MagicMock()
    mock_collection.get.return_value = {
        'metadatas': [
            {'title': 'Book A'},
            {'title': 'Book B'},
            {'title': 'Book C'}
        ]
    }
    mock_chroma_client.return_value.get_or_create_collection.return_value = mock_collection

    # Mock Oracle cursor and connection
    mock_cursor = MagicMock()
    # Simulate no existing books in DB
    mock_cursor.fetchone.side_effect = [None, None, None]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_oracle_connect.return_value = mock_conn

    # Import the script (runs the sync logic)
    sys.modules.pop("utils.sync_chromadb_to_oracle", None)
    importlib.import_module("utils.sync_chromadb_to_oracle")

    # Check that SELECT and INSERT were called for each book
    assert mock_cursor.execute.call_count == 6  # 3 SELECT + 3 INSERT
    assert mock_conn.commit.call_count == 3

@patch("chromadb.PersistentClient")
@patch("oracledb.connect")
@patch("dotenv.load_dotenv")
@patch("os.environ.get")
def test_sync_skips_existing_titles(mock_env_get, mock_load_dotenv, mock_oracle_connect, mock_chroma_client):
    """
    Test that the sync function skips inserting books into the Oracle database if their titles already exist.
    This test mocks environment variables, ChromaDB collection, and Oracle database connection.
    It simulates a scenario where both books retrieved from ChromaDB already exist in the Oracle database.
    The test asserts that only SELECT queries are executed to check for existence, and no INSERT or commit operations are performed.
    Args:
        mock_env_get: Mock for environment variable retrieval.
        mock_load_dotenv: Mock for dotenv loading.
        mock_oracle_connect: Mock for Oracle database connection.
        mock_chroma_client: Mock for ChromaDB client.
    """
    
    mock_env_get.side_effect = lambda k: {
        "DB_CONN_STRING": "fake_dsn",
        "DB_USER": "user",
        "DB_PASSWORD": "pass"
    }[k]

    mock_collection = MagicMock()
    mock_collection.get.return_value = {
        'metadatas': [
            {'title': 'Book X'},
            {'title': 'Book Y'}
        ]
    }
    mock_chroma_client.return_value.get_or_create_collection.return_value = mock_collection

    mock_cursor = MagicMock()
    # Simulate both books already exist
    mock_cursor.fetchone.side_effect = [(1,), (2,)]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_oracle_connect.return_value = mock_conn

    sys.modules.pop("utils.sync_chromadb_to_oracle", None)
    importlib.import_module("utils.sync_chromadb_to_oracle")

    # Only SELECTs, no INSERTs
    assert mock_cursor.execute.call_count == 2
    mock_conn.commit.assert_not_called()

@patch("chromadb.PersistentClient")
@patch("oracledb.connect")
@patch("dotenv.load_dotenv")
@patch("os.environ.get")
def test_sync_handles_missing_title_metadata(mock_env_get, mock_load_dotenv, mock_oracle_connect, mock_chroma_client):
    """
    Test that the sync function correctly handles metadata entries missing the 'title' key.
    This test mocks environment variables, ChromaDB collection, and Oracle database connection.
    It simulates a scenario where some metadata entries lack the 'title' field, ensuring that:
      - Only entries with a valid 'title' are processed for database insertion.
      - The correct number of database operations (SELECT and INSERT) are performed.
      - The database commit is called once after insertion.
    Args:
        mock_env_get: Mock for environment variable retrieval.
        mock_load_dotenv: Mock for dotenv loading.
        mock_oracle_connect: Mock for Oracle database connection.
        mock_chroma_client: Mock for ChromaDB client.
    """
    
    mock_env_get.side_effect = lambda k: {
        "DB_CONN_STRING": "fake_dsn",
        "DB_USER": "user",
        "DB_PASSWORD": "pass"
    }[k]

    mock_collection = MagicMock()
    mock_collection.get.return_value = {
        'metadatas': [
            {'not_title': 'No Title'},
            None,
            {'title': 'Book Z'}
        ]
    }
    mock_chroma_client.return_value.get_or_create_collection.return_value = mock_collection

    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [None]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_oracle_connect.return_value = mock_conn

    sys.modules.pop("utils.sync_chromadb_to_oracle", None)
    importlib.import_module("utils.sync_chromadb_to_oracle")

    # Only one valid title processed
    assert mock_cursor.execute.call_count == 2  # 1 SELECT + 1 INSERT
    assert mock_conn.commit.call_count == 1
    