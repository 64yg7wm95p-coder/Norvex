from dataclasses import dataclass, field


@dataclass
class UniversalProduct:
    source: str
    source_product_id: str
    original_title: str
    title: str
    description: str
    cost_price: float
    target_price: float
    images: list[str] = field(default_factory=list)
    status: str = "Hazır"