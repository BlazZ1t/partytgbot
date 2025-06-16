from pymongo import MongoClient
from dotenv import load_dotenv
import os

_client = None
_db = None

def init_db():
    global _client, _db
    load_dotenv()
    _client = MongoClient(os.getenv("MONGO_URI"))
    _db = _client["partybot"]

def get_users_col():
    if _db is None:
        raise RuntimeError("DB not initialized. Did you call init_db()?")
    return _db["users"]

def get_events_col():
    if _db is None:
        raise RuntimeError("DB not initialized. Did you call init_db()?")
    return _db["events"]

def get_invites_col():
    if _db is None:
        raise RuntimeError("DB not initialized. Did you call init_db()?")
    return _db["invites"]