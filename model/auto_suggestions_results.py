class Result:
    def __init__(self, keyword, suggestions):
        self.keyword = keyword
        self.suggestions = suggestions


def serialize_result(obj):
    if isinstance(obj, Result):
        return {"keyword": obj.keyword, "suggestions": obj.suggestions}
    raise TypeError(f"Object of type '{obj.__class__.__name__}' is not JSON serializable")
