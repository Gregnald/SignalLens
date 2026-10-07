"""Derives a product category from a Flipkart product name.

The source dataset (Dataset-SA.csv) has no category or seller column — only a free-text
product_name. This is a keyword-based heuristic categorizer, not ground truth; it exists so
the product catalog can be browsed by category. First matching rule wins, so order matters
(more specific terms before their broader parents, e.g. "laptop" before generic "computer").
"""

import re

_RULES: list[tuple[str, list[str]]] = [
    ("Mobiles & Tablets", [
        "mobile phone", "smartphone", " ipad", "iphone", "redmi", "poco", "realme",
        "oneplus", "vivo ", "oppo ", "samsung galaxy", "tablet", "mi 11", "mi 10",
        " 4g ", " 5g ",
    ]),
    ("Laptops & Computers", [
        "laptop", "macbook", "notebook", "chromebook", "desktop pc", "cpu cabinet",
        "keyboard", "mouse", " ssd", "monitor", "printer", "cartridge", "webcam",
        "pen drive", "pendrive", "hard disk", "memory card", "microsd",
    ]),
    ("TVs & Home Entertainment", [
        "led tv", "smart tv", "television", "home theatre", "soundbar", "projector",
        "dth", "set top box", "remote",
    ]),
    ("Cameras & Accessories", ["dslr", "camera", "tripod", "gimbal", "lens kit"]),
    ("Audio & Wearables", [
        "headphone", "earphone", "earbud", "neckband", "bluetooth speaker",
        "smartwatch", "fitness band", "power bank", "headset", "bluetooth device",
    ]),
    ("Watches & Jewellery", ["watch", "bracelet", "jewellery", "jewelry", "necklace", "ring "]),
    ("Large Appliances", [
        "refrigerator", "washing machine", "air conditioner", " ac ", "geyser",
        "water heater", "dishwasher",
    ]),
    ("Kitchen Appliances", [
        "mixer", "juicer", "grinder", "microwave", "induction", "electric kettle",
        "toaster", "rice cooker", "sandwich maker", "air fryer", "oven", "cooker",
        "chimney", "food processor", "food factory", "blender",
    ]),
    ("Home Comfort & Cleaning", [
        "fan", "cooler", "humidifier", "air purifier", "vacuum cleaner", "iron ",
        "dry iron", "mop", "water purifier", "ro ",
    ]),
    ("Furniture", [
        "chair", "table", "sofa", "bed ", "mattress", "wardrobe", "bookshelf",
        "book shelf", "cabinet", "desk ", "stool", "rack",
    ]),
    ("Home Decor", [
        "curtain", "cushion", "vase", "wall decor", "wall art", "showpiece",
        "photo frame", "lamp", "light", "candle", "plant", "bamboo",
    ]),
    ("Kitchen & Dining", [
        "dinner set", "cookware", "pan", "kettle", "flask", "bottle", "lunch box",
        "crockery", "opalware", "casserole", "storage container",
    ]),
    ("Clothing & Fashion", [
        "kurta", "saree", "dupatta", "shirt", "t-shirt", "tshirt", "jeans",
        "trouser", "cargo", "dress", "jacket", "sweater", "hoodie", "ethnic wear",
    ]),
    ("Footwear", ["shoes", "sandal", "slipper", "sneaker", "footwear", "flip flop"]),
    ("Beauty & Personal Care", [
        "kajal", "lipstick", "makeup", "cream", "shampoo", "hair oil", "perfume",
        "deodorant", "face wash", "skincare", "trimmer", "hair dryer", "razor",
    ]),
    ("Sports & Fitness", [
        "football", "cricket", "stumps", "badminton", "yoga", "dumbbell", "gym",
        "swimming", "skateboard", "skate", "cycling", "fitness", "exercise",
        "wrist support", "knee support", "tummy trimmer",
    ]),
    ("Toys & Baby", ["toy", "baby", "kids", "infant", "diaper", "stroller"]),
    ("Automotive", [
        "car cover", "bike ", "two wheeler", "vehicle", "helmet", "car accessory",
        "car charger", "car light", "motorcycle",
    ]),
    ("Books & Stationery", ["book", "paperback", "hardcover", "pencil", " pen ", "notebook set"]),
    ("Tools & Hardware", ["drill", "wrench", "screwdriver", "tool kit", "hardware"]),
    ("Garden & Outdoors", ["seeds", "garden", "plant pot", "outdoor"]),
]

_OTHER = "Other"


def categorize_product(product_name: str) -> str:
    if not product_name:
        return _OTHER
    name = f" {product_name.lower()} "
    name = re.sub(r"[^\w\s]", " ", name)
    for category, keywords in _RULES:
        for kw in keywords:
            if kw in name:
                return category
    return _OTHER


def clean_product_name(product_name: str) -> str:
    """Strips mojibake/encoding-artifact runs commonly found in this scraped dataset."""
    if not product_name:
        return product_name
    cleaned = re.sub(r"[ÃÂÐÒÓ®]{2,}", " ", product_name)
    cleaned = re.sub(r"\?{3,}", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned
