from icrawler.builtin import GoogleImageCrawler
import os

# Define search terms for each damaged furniture category
search_terms = [
    "broken bench",
    "damaged street sign",
    "broken lamp post",
    "damaged bus stop shelter",
    "broken playground equipment"
]

# Output folder
output_dir = "urban_furniture_dataset"
os.makedirs(output_dir, exist_ok=True)

# Number of images to download per class
images_per_class = 50

# Download function
for term in search_terms:
    print(f"🔎 Downloading: {term}")
    class_folder = os.path.join(output_dir, term.replace(" ", "_"))
    os.makedirs(class_folder, exist_ok=True)
    
    crawler = GoogleImageCrawler(storage={"root_dir": class_folder})
    crawler.crawl(keyword=term, max_num=images_per_class)

print("✅ All images downloaded using icrawler!")
