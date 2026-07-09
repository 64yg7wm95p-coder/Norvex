from .product import UniversalProduct
from .pricing import PricingEngine
from .ai import AIEngine


class ProductPipeline:
    def __init__(self):
        self.pricing_engine = PricingEngine()
        self.ai_engine = AIEngine()

    def process(self, product: UniversalProduct) -> UniversalProduct:
        product = self.ai_engine.apply(product)
        product = self.pricing_engine.apply(product)

        return product