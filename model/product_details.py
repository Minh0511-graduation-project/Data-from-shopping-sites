class ProductDetails:
    def __init__(self, name, price):
        self.name = name
        self.price = price


def serialize_result(obj):
    if isinstance(obj, ProductDetails):
        return {"name": obj.name, "price": obj.price}
    raise TypeError(f"Object of type '{obj.__class__.__name__}' is not JSON serializable")
