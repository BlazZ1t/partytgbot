telegram_party_bot/
├── bot/
│   ├── __init__.py
│   ├── main.py               # Entry point
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── registration.py   # Name/surname collection
│   │   ├── event_creation.py # Host creates event
│   │   ├── link_generation.py # Handles invite links
│   │   └── admin.py          # Admin commands
│   ├── database/
│   │   ├── __init__.py
│   │   └── mongo.py          # MongoDB logic and collections
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py           # User schema (BaseModel)
│   │   └── event.py          # Event schema (BaseModel)
│   └── utils/
│       ├── __init__.py
│       ├── links.py          # Invite link generation/validation
│       ├── time.py           # Expiry checks and timestamps
│       └── permissions.py    # Admin checks, host checks
├── .env                      # Contains BOT_TOKEN, DB credentials, ADMIN_IDS
├── docker-compose.yml       # MongoDB, bot container
├── Dockerfile               # Bot Dockerfile
├── requirements.txt         # python-telegram-bot, pymongo, etc.
└── README.md
