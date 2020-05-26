# [Weedmaps.com](https://www.freelancer.com/users/l.php?url=https:%2F%2Fweedmaps.com%2Fdispensaries%2Fin%2Funited-states%2Fcalifornia%2F&sig=cec6a24e07e00ea422667b4bd9253f79c6fee1a59aacfd5444be27579cd426d2) Listings Scraper

> This bot scrapes all the listings and the listing info in a region.

![](screenshot.png)

# Install

Clone the repository:

```bash
git clone https://github.com/skdcodes/freelancer-python-luminati-weedmaps.git
cd freelancer-python-luminati-weedmaps
```

You require `python3` and `pip3` installed. Install the python dependencies by running:

```bash
pip3 install -r requirements.txt
```

# Usage

Run the script:

```bash
python3 scrape.py
```

# Features

- For an arbitrary GeoPoint and Radius, at max `10,000` listings can be retrieved and their information stored.

  ```python
  # scrape.py

  CENTER = {"lat": 34.04871368408203, "lng": -118.2420196533203}
  RADIUS = 100
  ```

- Threading is implemented. By default `20` requests are performed at time.

  ```python
  # scrape.py

  MAX_WORKERS = 20
  ```

- A rotating proxy service is of paramount importance. I've used [Luminati.io](https://luminati.io/) service for this purpose to burst down requests.

  ```python
  # scrape.py

  PROXIES = {
      'http': 'http://lum-customer-hl_233xze5-zone-static:g32kc5833f20t@zproxy.lum-superproxy.io:22225',
      'https': 'http://lum-customer-hl_233xze5-zone-static:g32kc5833f20t@zproxy.lum-superproxy.io:22225',
  }
  ```

# Notes

- The listings search uses Elasticsearch, therefore a maximum of `10,000` listings can be retrieved.
- Only `User-Agent` has to be set to cloak your bot.
- Rate limiting per IP is implemented. Therefore a service like [Luminati.io](https://luminati.io/) is very essential to burst down requests.
