from flask import Flask, render_template, request, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def scrape_listing(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        address = page.locator('.listingAddress').first.text_content()
        price = page.locator('.listingPrice').first.text_content()
        beds = page.locator('li:has-text("Bedrooms")').first.text_content()
        baths = page.locator('li:has-text("Bathrooms")').first.text_content()
        image = page.locator('img').first.get_attribute('src')

        browser.close()
        return {
            'address': address.strip() if address else "N/A",
            'price': price.strip() if price else "N/A",
            'beds': beds.strip() if beds else "N/A",
            'baths': baths.strip() if baths else "N/A",
            'img': image
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    url = request.json.get('url')
    try:
        data = scrape_listing(url)
        caption = f"🏡 {data['address']}\n💰 {data['price']}\n🛏 {data['beds']} | 🛁 {data['baths']}\n🔗 {url}"
        return jsonify({'caption': caption, 'image': data['img']})
    except Exception as e:
        print("ERROR:", e)
        return jsonify({'error': str(e)}), 500
