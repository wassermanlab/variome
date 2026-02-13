from constants import NA

def validate_get(v, index):
    if v is [] or v is None:
        return NA
    if not isinstance(v, list):
        if v == 0:
            return "0"
        return v
    if len(v) <= index:
        return NA
    val = v[index]
    
    if isinstance(val, float) and float(val).is_integer():
        return str(val).replace('.0', '')
    
    elif isinstance(val, str):
      if val == "" or val is None:
        return NA
      else:
        return val
    if val in [None, ""]:
        return NA
    
    return val