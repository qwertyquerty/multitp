import ctypes

class Diff:
    def __init__(self, path, old, new):
        self.path = path
        self.old = old
        self.new = new

    def __str__(self):
        return f"{self.path}: {self.old!r} -> {self.new!r}"

    def __repr__(self):
        return f"Diff(path={self.path!r}, old={self.old!r}, new={self.new!r})"
    
    def to_dict(self):
        return {"path": self.path, "old": self.old, "new": self.new}

def deep_diff(a, b, path=""):
    diffs = []

    if isinstance(a, dict) and isinstance(b, dict):
        for key in a:  # keys guaranteed same
            new_path = f"{path}.{key}" if path else key
            diffs.extend(deep_diff(a[key], b[key], new_path))

    elif isinstance(a, list) and isinstance(b, list):
        for i, (v1, v2) in enumerate(zip(a, b)):  # lengths guaranteed same
            new_path = f"{path}[{i}]"
            diffs.extend(deep_diff(v1, v2, new_path))

    else:
        if a != b:
            diffs.append(Diff(path, a, b))

    return diffs

def ctypes_to_dict(obj):
    """Recursively convert a ctypes Structure to a dict."""
    if isinstance(obj, ctypes.Array):
        return [ctypes_to_dict(item) for item in obj]

    elif isinstance(obj, ctypes.Structure):
        result = {}
        for field_name, _ in obj._fields_:
            value = getattr(obj, field_name)
            result[field_name] = ctypes_to_dict(value)
        return result

    elif isinstance(obj, ctypes._Pointer):
        if obj:
            return ctypes_to_dict(obj.contents)
        else:
            return None

    else:
        return obj
