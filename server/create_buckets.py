import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

buckets = supabase.storage.list_buckets()
bucket_names = [b.name for b in buckets]

for bucket_name in ["exam-pdfs", "answer-images"]:
    if bucket_name not in bucket_names:
        print(f"Creating bucket: {bucket_name}")
        supabase.storage.create_bucket(bucket_name, {"public": False})
    else:
        print(f"Bucket {bucket_name} already exists.")
