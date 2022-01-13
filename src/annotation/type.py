from typing import Any, Callable, Dict, Optional

from typing_extensions import Literal

OptionalQuery = Optional[Dict[str, Any]]
RetrieveCallback = Callable[[Dict[str, Any]], str]
PartOfSpeach = Literal["名詞", "固有名詞", "形容詞"]
