class ProductDetails:
    def __init__(self, name, price, image_url):
        self.image_url = image_url
        self.name = name
        self.price = price


def serialize_result(obj):
    if isinstance(obj, ProductDetails):
        return {"image_url": obj.image_url, "name": obj.name, "price": obj.price}
    raise TypeError(f"Object of type '{obj.__class__.__name__}' is not JSON serializable")
