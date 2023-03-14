class ProductDetails:
    def __init__(self, site, searchTerm, name, price, imageUrl, updatedAt):
        self.site = site
        self.searchTerm = searchTerm
        self.imageUrl = imageUrl
        self.name = name
        self.price = price
        self.updatedAt = updatedAt


def serialize_product(obj):
    if isinstance(obj, ProductDetails):
        return {"site": obj.site, "searchTerm": obj.searchTerm, "imageUrl": obj.imageUrl, "name": obj.name,
                "price": obj.price, "updatedAt": obj.updatedAt}
    raise TypeError(f"Object of type '{obj.__class__.__name__}' is not JSON serializable")
