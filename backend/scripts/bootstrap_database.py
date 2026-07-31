"""
Database bootstrap script.
Creates the database, tables, and schema.
"""
import sys
import os
import psycopg2
from psycopg2 import sql
from app.core.config import settings
from app.core.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


def create_database():
    """Create the PostgreSQL database if it doesn't exist."""
    # Parse the database URL to extract connection details
    db_url_parts = settings.DATABASE_URL.split("//")[1]
    db_host_port = db_url_parts.split("@")[1]
    db_host = db_host_port.split(":")[0]
    db_port = db_host_port.split(":")[1].split("/")[0]
    db_name = db_url_parts.split("/")[-1]
    db_user = db_url_parts.split("@")[0].split(":")[0]
    db_password = db_url_parts.split("@")[0].split(":")[1]
    
    logger.info("Creating database", extra_data={"database": db_name})
    
    try:
        # Connect to PostgreSQL default database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database="postgres",
            user=db_user,
            password=db_password
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            sql.SQL("SELECT 1 FROM pg_database WHERE datname = {}").format(
                sql.Literal(db_name)
            )
        )
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(db_name)
                )
            )
            logger.info("Database created successfully", extra_data={"database": db_name})
        else:
            logger.info("Database already exists", extra_data={"database": db_name})
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error("Error creating database", extra_data={"error": str(e)})
        raise


def run_migrations():
    """Run Alembic migrations to create tables."""
    logger.info("Running database migrations")
    
    try:
        import subprocess
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("Migrations completed successfully")
        else:
            logger.error("Migration failed", extra_data={"stderr": result.stderr})
            raise Exception(f"Migration failed: {result.stderr}")
            
    except Exception as e:
        logger.error("Error running migrations", extra_data={"error": str(e)})
        raise


if __name__ == "__main__":
    try:
        create_database()
        run_migrations()
        logger.info("Database bootstrap completed successfully")
    except Exception as e:
        logger.error("Database bootstrap failed", extra_data={"error": str(e)})
        sys.exit(1)
