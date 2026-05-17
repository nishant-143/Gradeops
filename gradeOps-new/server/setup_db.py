import os
import glob
import psycopg2
from dotenv import load_dotenv

def main():
    print("Loading environment variables...")
    load_dotenv()
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not found in .env")
        return

    print("Connecting to database...")
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        migrations_dir = os.path.join(os.path.dirname(__file__), "..", "supabase", "migrations")
        files = sorted(glob.glob(os.path.join(migrations_dir, "*.sql")))
        
        if not files:
            print(f"No SQL files found in {migrations_dir}")
            return
            
        print(f"Found {len(files)} migration files. Executing...")
        
        for file_path in files:
            filename = os.path.basename(file_path)
            print(f"Running {filename}...")
            with open(file_path, "r", encoding="utf-8") as f:
                sql = f.read()
                try:
                    cursor.execute(sql)
                    print(f"  [SUCCESS] {filename} executed successfully")
                except Exception as e:
                    print(f"  [ERROR] Error executing {filename}: {e}")
                    # Keep going or stop? Let's stop on error to be safe
                    return
                    
        print("\nAll database migrations applied successfully! You can now start the server.")
        
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
