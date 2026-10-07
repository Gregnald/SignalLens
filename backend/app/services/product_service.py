from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.feedback_unit import FeedbackUnit
from app.models.review import Review
from app.models.theme import Theme
from app.schemas.product import CategoryOut, ProductDetail, ProductSummary, ThemeMention
from app.utils.metrics import safe_mean


def list_categories(db: Session, dataset_id: int) -> list[CategoryOut]:
    rows = (
        db.query(
            Review.product_category,
            func.count(func.distinct(Review.product_name)).label("product_count"),
            func.count(Review.id).label("review_count"),
            func.avg(Review.rating).label("avg_rating"),
        )
        .filter(Review.dataset_id == dataset_id, Review.product_category.isnot(None))
        .group_by(Review.product_category)
        .order_by(func.count(Review.id).desc())
        .all()
    )
    return [
        CategoryOut(
            category=r.product_category,
            product_count=r.product_count,
            review_count=r.review_count,
            avg_rating=round(r.avg_rating, 2) if r.avg_rating is not None else None,
        )
        for r in rows
    ]


def list_products(db: Session, dataset_id: int, category: str | None = None) -> list[ProductSummary]:
    query = db.query(Review).filter(Review.dataset_id == dataset_id, Review.product_name.isnot(None))
    if category:
        query = query.filter(Review.product_category == category)
    reviews = query.all()

    by_product: dict[str, list[Review]] = {}
    for r in reviews:
        by_product.setdefault(r.product_name, []).append(r)

    summaries = []
    for name, items in by_product.items():
        ratings = [r.rating for r in items if r.rating is not None]
        prices = [r.product_price for r in items if r.product_price is not None]
        negative = sum(1 for r in items if r.rating is not None and r.rating <= 2)
        summaries.append(
            ProductSummary(
                product_name=name,
                category=items[0].product_category,
                review_count=len(items),
                avg_rating=round(safe_mean(ratings), 2) if ratings else None,
                avg_price=round(safe_mean(prices), 2) if prices else None,
                negative_percent=round(100.0 * negative / len(items), 1) if items else 0.0,
            )
        )

    return sorted(summaries, key=lambda s: -s.review_count)


def get_product_detail(db: Session, dataset_id: int, product_name: str) -> ProductDetail | None:
    reviews = (
        db.query(Review)
        .filter(Review.dataset_id == dataset_id, Review.product_name == product_name)
        .all()
    )
    if not reviews:
        return None

    ratings = [r.rating for r in reviews if r.rating is not None]
    prices = [r.product_price for r in reviews if r.product_price is not None]
    negative_count = sum(1 for r in reviews if r.rating is not None and r.rating <= 2)

    review_ids = [r.id for r in reviews]
    units = db.query(FeedbackUnit).filter(FeedbackUnit.review_id.in_(review_ids)).all() if review_ids else []

    sentiment_breakdown = {"positive": 0, "neutral": 0, "negative": 0}
    for u in units:
        if u.sentiment in sentiment_breakdown:
            sentiment_breakdown[u.sentiment] += 1

    rating_distribution: dict[str, int] = {}
    for r in reviews:
        if r.rating is not None:
            key = str(int(r.rating))
            rating_distribution[key] = rating_distribution.get(key, 0) + 1

    theme_ids = {u.theme_id for u in units if u.theme_id}
    related_themes = []
    if theme_ids:
        themes = db.query(Theme).filter(Theme.id.in_(theme_ids)).all()
        theme_mention_counts = {}
        for u in units:
            if u.theme_id:
                theme_mention_counts[u.theme_id] = theme_mention_counts.get(u.theme_id, 0) + 1
        for t in themes:
            related_themes.append(
                ThemeMention(
                    theme_id=t.id,
                    theme_name=t.name,
                    severity=t.severity or "low",
                    mention_count=theme_mention_counts.get(t.id, 0),
                )
            )
        related_themes.sort(key=lambda t: -t.mention_count)

    sorted_by_rating = sorted(reviews, key=lambda r: (r.rating if r.rating is not None else 3))
    negative_reviews = [r.clean_text or r.raw_text for r in sorted_by_rating[:5]]
    representative_reviews = [r.clean_text or r.raw_text for r in reviews[:8]]

    return ProductDetail(
        product_name=product_name,
        category=reviews[0].product_category,
        review_count=len(reviews),
        avg_rating=round(safe_mean(ratings), 2) if ratings else None,
        avg_price=round(safe_mean(prices), 2) if prices else None,
        sentiment_breakdown=sentiment_breakdown,
        rating_distribution=rating_distribution,
        representative_reviews=representative_reviews,
        negative_reviews=negative_reviews,
        related_themes=related_themes[:10],
    )
