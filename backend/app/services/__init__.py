from app.services.authentication import AuthService
from app.services.convert_utils import convert_datetime_to_pydantic_string as datetime_to_string
from app.services.convert_utils import convert_pydantic_string_to_datetime as string_to_datetime

auth_service = AuthService()
