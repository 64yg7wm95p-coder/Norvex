import requests


class AddaxSupplier:
    BASE_URL = "https://addax.co.uk"

    def get_products(self, collection="newest-products", limit=10):
        url = f"{self.BASE_URL}/collections/{collection}/products.json?limit={limit}"

        response = requests.get(url, timeout=20)
        response.raise_for_status()

        data = response.json()
        products = []

        for item in data.get("products", []):
            variant = item["variants"][0]
            image = item["images"][0]["src"] if item.get("images") else None

            cost_price = float(variant["price"])

            products.append({
                "supplier": "addax_uk",
                "title": item["title"],
                "handle": item["handle"],
                "url": f"{self.BASE_URL}/products/{item['handle']}",
                "cost_price": cost_price,
                "image": image,
                "variants": item["variants"],
                "body_html": item.get("body_html", "")
            })

        return products