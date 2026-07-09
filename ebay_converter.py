import pandas as pd

INPUT_FILE = "addax_filtered_products.csv"
OUTPUT_FILE = "ebay_upload_ready.csv"

df = pd.read_csv(INPUT_FILE).head(5)

LOCATION = "London"

def clean(value):
    if pd.isna(value):
        return ""
    return str(value).strip()

if "*Description" in df.columns:
    df["*Description"] = df["*Description"].astype(str).str.replace("\n", " ", regex=False)

df["*Location"] = LOCATION
df["*Duration"] = "GTC"
df["*Quantity"] = 5
df["*DispatchTimeMax"] = 1

df["Brand"] = df["Brand"].apply(clean)
df["Brand"] = df["Brand"].replace("", "Unbranded")

df["MPN"] = "Does Not Apply"
df["EAN"] = "Does Not Apply"
df["UPC"] = "Does Not Apply"

df["Product:EAN"] = "Does Not Apply"
df["Product:MPN"] = "Does Not Apply"
df["ExternalProductID.Type"] = "EAN"
df["ExternalProductID.Value"] = "Does Not Apply"

df["Department"] = "Women"
df["Colour"] = df["Colour"].apply(clean) if "Colour" in df.columns else ""
df["Size"] = df["Size"].apply(clean) if "Size" in df.columns else ""
df["Style"] = df["Style"].apply(clean) if "Style" in df.columns else ""

df["Colour"] = df["Colour"].replace("", "Multicoloured")
df["Size"] = df["Size"].replace("", "Regular")
df["Style"] = df["Style"].replace("", "Casual")

df["Type"] = "Trousers"
df["Material"] = "Polyester"
df["Fit"] = "Regular"
df["Occasion"] = "Casual"
df["Season"] = "All Seasons"

df = df.fillna("")

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print("eBay upload dosyası hazır:")
print(OUTPUT_FILE)
print(f"{len(df)} ürün yazıldı.")