from pydantic import BaseModel


class CategoryOut(BaseModel):
    category: str
    product_count: int
    review_count: int
    avg_rating: float | None


class ProductSummary(BaseModel):
    product_name: str
    category: str | None
    review_count: int
    avg_rating: float | None
    avg_price: float | None
    negative_percent: float


class ThemeMention(BaseModel):
    theme_id: int
    theme_name: str
    severity: str
    mention_count: int


class ProductDetail(BaseModel):
    product_name: str
    category: str | None
    review_count: int
    avg_rating: float | None
    avg_price: float | None
    sentiment_breakdown: dict[str, int]
    rating_distribution: dict[str, int]
    representative_reviews: list[str]
    negative_reviews: list[str]
    related_themes: list[ThemeMention]
