def calculate_ebay_price(cost: float) -> float:
    """
    Shopify maliyet fiyatından eBay satış fiyatını hesaplar.
    """

    return round((cost * 1.35) + 2.00, 2)