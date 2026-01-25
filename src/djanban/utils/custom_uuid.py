import base64
import uuid


# Custom uuid used for some elements
def custom_uuid():
    # _uuid = uuid.uuid1().bytes.encode('base64').rstrip('=\n').replace('/', '_')
    # Python 3 compatibility
    _uuid = (
        base64.b64encode(uuid.uuid1().bytes)
        .decode("utf-8")
        .rstrip("=\n")
        .replace("/", "_")
    )
    return _uuid
