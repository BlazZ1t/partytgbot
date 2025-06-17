from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bot.models.user import User
from pathlib import Path

_client = None
_db = None

def init_db():
    global _client, _db
    if Path(".env.dev").exists():
        load_dotenv(".env.dev")
    else:
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

def get_paginated_users(page: int, page_size: int = 5):
    users_col = get_users_col()
    skip = (page - 1) * page_size
    users_cursor = users_col.find().skip(skip).limit(page_size)
    return [User(**doc) for doc in users_cursor]

def count_users():
    return get_users_col().count_documents({})