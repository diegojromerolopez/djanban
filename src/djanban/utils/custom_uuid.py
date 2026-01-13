import base64
import uuid


# Custom uuid used for some elements
def custom_uuid():
    _uuid = (
        base64.b64encode(uuid.uuid1().bytes)
        .decode("ascii")
        .rstrip("=\n")
        .replace("/", "_")
    )
    return _uuid
