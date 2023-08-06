from datetime import datetime


def convert_pydantic_string_to_datetime(string: str) -> datetime:
    return datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%f')


def convert_datetime_to_pydantic_string(timestamp: datetime) -> str:
    return timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')
