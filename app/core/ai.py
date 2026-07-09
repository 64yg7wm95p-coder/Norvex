from .product import UniversalProduct


class AIEngine:
    """
    Xathes AI motoru.

    Şimdilik demo modda çalışır.
    Daha sonra OpenAI entegrasyonu burada yapılacak.
    """

    def optimize_title(self, title: str) -> str:
        if not title:
            return ""

        return title.strip()

    def optimize_description(self, description: str) -> str:
        if not description:
            return ""

        return description.strip()

    def apply(self, product: UniversalProduct) -> UniversalProduct:
        product.title = self.optimize_title(product.title)
        product.description = self.optimize_description(product.description)

        return product