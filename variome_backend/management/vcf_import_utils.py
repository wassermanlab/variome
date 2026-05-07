def validate_get(v, index, na="."):
    if not v or v is None:
        return na
    if not isinstance(v, list):
        if v == 0:
            return "0"
        return v
    if len(v) <= index:
        return na
    val = v[index]

    if isinstance(val, float) and float(val).is_integer():
        return str(val).replace('.0', '')

    elif isinstance(val, str):
        if val == "" or val is None:
            return na
        else:
            return val
    if val in [None, ""]:
        return na

    return val
