
import uuid


# Custom uuid used for some elements
def custom_uuid():
    _uuid = uuid.uuid1().bytes.encode('base64').rstrip('=\n').replace('/', '_')
    return _uuid