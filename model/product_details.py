class ProductDetails:
    def __init__(self, search_term, name, price, image_url):
        self.search_term = search_term
        self.image_url = image_url
        self.name = name
        self.price = price


def serialize_result(obj):
    if isinstance(obj, ProductDetails):
        return {"search_term": obj.search_term, "image_url": obj.image_url, "name": obj.name, "price": obj.price}
    raise TypeError(f"Object of type '{obj.__class__.__name__}' is not JSON serializable")
