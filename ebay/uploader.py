from ebay.inventory import create_inventory
from ebay.offer import create_offer
from ebay.publish import publish_offer


def upload_product_to_ebay(product, seo):

    print("\n====================================")
    print("eBay Upload Başladı")
    print("====================================")

    print("AI Title:", seo["title"])
    print("eBay Price:", product["ebay_price"])

    # Inventory oluştur
    create_inventory(product, seo)

    # AI açıklamasını ürüne ekle
    product["ai_description"] = seo.get("description", "")

    # Offer oluştur
    offer_id = create_offer(product)

    print("Offer ID:", offer_id)

    # Publish et
    listing_id = publish_offer(product)

    print("\n====================================")
    print("İlan Başarıyla Yayınlandı!")
    print("Listing ID:", listing_id)
    print("====================================")