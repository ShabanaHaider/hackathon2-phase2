"""
Simple script to clear conversations from the database.
Run: python clear_conversation.py
"""
import os
from dotenv import load_dotenv
from sqlmodel import Session, create_engine, text

load_dotenv()

def clear_conversations():
    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return

    # Use sync engine (keep postgresql://, not asyncpg)
    if "asyncpg" in database_url:
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    engine = create_engine(database_url)

    with Session(engine) as session:
        # Delete all messages first (foreign key)
        result = session.exec(text("DELETE FROM messages"))
        msg_count = result.rowcount
        print(f"Deleted {msg_count} messages")

        # Delete all conversations
        result = session.exec(text("DELETE FROM conversations"))
        conv_count = result.rowcount
        print(f"Deleted {conv_count} conversations")

        session.commit()

    print("Done! Refresh your browser to start fresh.")

if __name__ == "__main__":
    clear_conversations()
