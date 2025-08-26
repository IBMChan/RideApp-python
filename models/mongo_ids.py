from bson import ObjectId

def to_objectid(val):
    if isinstance(val, ObjectId):
        return val
    try:
        return ObjectId(val)
    except Exception:
        return None
