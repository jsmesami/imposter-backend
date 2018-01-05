
def deepmerge(source: dict, destination: dict) -> dict:
    """
    Recursively merge source dictionary into destination.
    Use `reduce(deepmerge, [d1, d2, d3])` to merge multiple dictionaries
    """
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            deepmerge(value, node)
        else:
            destination[key] = value

    return destination
