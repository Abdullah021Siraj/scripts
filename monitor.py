import requests
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("monitor.log"), logging.StreamHandler()]
)

# Endpoints to monitor
VERCEL_URL = "https://url-shortener-nu-lilac.vercel.app"
AWS_URL = "https://rcefn1q34m.execute-api.eu-central-1.amazonaws.com/prod"

def check_endpoint(name, url, expected_status=200):
    """Check if an endpoint is up and responding correctly."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == expected_status:
            logging.info(f"[OK] {name} is healthy ({response.status_code})")
            return True
        else:
            logging.error(f"[FAIL] {name} returned {response.status_code}")
            return False
    except requests.RequestException as e:
        logging.error(f"[ERROR] {name} check failed: {e}")
        return False

def monitor():
    """Continuously monitor services."""
    while True:
        logging.info("---- Running health checks ----")
        
        # 1. Check Vercel root
        check_endpoint("Vercel Root", VERCEL_URL)

        # 2. Check AWS API root (should respond, even if 403/404 is expected)
        check_endpoint("AWS API Root", AWS_URL, expected_status=403)

        # 3. Test Shortener flow (deep check)
        try:
            payload = {"url": "https://example.com"}
            r = requests.post(f"{VERCEL_URL}/api/shorten", json=payload, timeout=5)
            
            if r.status_code in (200, 201):
                data = r.json()
                short_url = data.get("shortUrl") or data.get("shortened_url")
                
                if short_url:
                    logging.info(f"[OK] Shortener created: {short_url}")
                    
                    # Test redirect
                    r2 = requests.get(short_url, allow_redirects=False, timeout=5)
                    if r2.status_code in (301, 302) and "Location" in r2.headers:
                        logging.info(f"[OK] Redirect works → {r2.headers['Location']}")
                    else:
                        logging.error(f"[FAIL] Redirect broken at {short_url}")
                else:
                    logging.error(f"[FAIL] No short URL in response: {data}")
            else:
                logging.error(f"[FAIL] Failed to create short URL: {r.status_code} {r.text}")
        
        except Exception as e:
            logging.error(f"[ERROR] Shortener flow failed: {e}")

        seconds_in_month = 30 * 24 * 60 * 60
        # Wait before next check
        time.sleep(seconds_in_month)  # check every 30 seconds

if __name__ == "__main__":
    monitor()
