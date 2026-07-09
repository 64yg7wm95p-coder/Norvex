# SupplierScanner Architecture

## Amaç

SupplierScanner, Shopify altyapısı kullanan tedarikçi sitelerinden ürünleri çekip AI ile optimize ederek eBay UK, Amazon UK ve Etsy gibi marketplace'lere otomatik yükleyen ve fiyat/stok senkronizasyonu yapan bir sistemdir.

## Temel Akış

Shopify Supplier Site  
↓  
Product Object  
↓  
AI Listing Generator  
↓  
Pricing Engine  
↓  
Database  
↓  
Marketplace Upload  
↓  
Sync Engine  

## Product Object Standardı

Her tedarikçiden gelen ürün şu formata çevrilir:

```json
{
  "supplier_name": "Addax UK",
  "supplier_site": "https://addax.co.uk",
  "supplier_product_url": "",
  "shopify_product_id": "",
  "shopify_variant_id": "",
  "title": "",
  "description": "",
  "cost_price": 0.0,
  "currency": "GBP",
  "stock": 1,
  "images": [],
  "variants": []
}