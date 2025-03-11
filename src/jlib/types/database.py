from typing import Literal

IsolationLevelType = Literal[
    "SERIALIZABLE",
    "REPEATABLE READ",
    "READ COMMITTED",
    "READ UNCOMMITTED",
    "AUTOCOMMIT",
]
