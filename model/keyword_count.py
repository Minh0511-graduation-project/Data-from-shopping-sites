class KeywordCount:
    def __init__(self, site, keyword, count, updatedAt):
        self.site = site
        self.keyword = keyword
        self.count = count
        self.updatedAt = updatedAt


def serialize_keyword_count(obj):
    if isinstance(obj, KeywordCount):
        return {"site": obj.site, "keyword": obj.keyword, "count": obj.count, "updatedAt": obj.updatedAt}
    raise TypeError(f"Object of type '{obj.__class__.__name__}' is not JSON serializable")
