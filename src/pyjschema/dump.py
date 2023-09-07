import base64
import json
from datetime import datetime, timedelta
from typing import Optional

import uuid


def dumps(obj, schema: Optional[dict] = None, **kwargs) -> str:
    return json.dumps(obj, default=_encoder, **kwargs)


def _encoder(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()

    elif isinstance(obj, timedelta):
        # TODO: CAUTION! datetime does not support nanoseconds
        return obj.total_seconds()

    elif isinstance(obj, uuid.UUID):
        return str(obj)

    elif isinstance(obj, bytes):
        return base64.b64encode(obj).decode()

    return json.dumps(obj)
