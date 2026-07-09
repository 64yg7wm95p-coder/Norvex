from .product import UniversalProduct


class PricingEngine:
    def __init__(
        self,
        markup: float = 1.35,
        fixed_fee: float = 2.00
    ):
        self.markup = markup
        self.fixed_fee = fixed_fee

    def calculate_price(self, cost: float) -> float:
        return round((cost * self.markup) + self.fixed_fee, 2)

    def apply(self, product: UniversalProduct) -> UniversalProduct:
        product.target_price = self.calculate_price(product.cost_price)
        return product