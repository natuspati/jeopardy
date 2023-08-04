from app.db.repositories.categories import COLLECTION_CONFIG as CATEGORY_CONFIG
from app.db.repositories.lobbies import COLLECTION_CONFIG as LOBBY_CONFIG
from app.db.repositories.players import COLLECTION_CONFIG as PLAYER_CONFIG
from app.db.repositories.questions import COLLECTION_CONFIG as QUESTION_CONFIG
from app.db.repositories.users import COLLECTION_CONFIG as USER_CONFIG

COLLECTION_CONFIGS = (
    CATEGORY_CONFIG, LOBBY_CONFIG, PLAYER_CONFIG, QUESTION_CONFIG, USER_CONFIG
)
