class Result:
    def __init__(self, site, keyword, suggestions, updatedAt):
        self.site = site
        self.keyword = keyword
        self.suggestions = suggestions
        self.UpdateAt = updatedAt


def serialize_suggestion(obj):
    if isinstance(obj, Result):
        return {"site": obj.site, "keyword": obj.keyword, "suggestions": obj.suggestions, "updatedAt": obj.UpdateAt}
    raise TypeError(f"Object of type '{obj.__class__.__name__}' is not JSON serializable")
