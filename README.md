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

After the script is complete, an excel sheet will be created at `dumps/data.xlsx`

# Features

- You can choose to scrape listings by either `region` or a GeoPoint `pin`. Either of the options can be set by modifying the variable `GATHER_TYPE = "pin"` and `GATHER_TYPE= "region"` as below:

  ```python
  # scrape.py

  GATHER_TYPE = "region"
  ```

  When `region` is chosen, only the variables `REGION` and `RADIUS` are considered.

  When `pin` is chosen, only variables `CENTER` and `RADIUS` are considered.

- The `REGION` variable is the region "slug" from which you would like to scrape listings. For example, in order to scrape for [all locations](https://api-g.weedmaps.com/wm/v1/regions/earth/subregions) one would be set `REGION = "earth"`. Similarly, for a more specific region, say [California](https://api-g.weedmaps.com/wm/v1/regions/california/subregions), one should set `REGION = "california"`

  ```python
  # scrape.py

  REGION = "california"
  RADIUS = 75
  ```

- The `CENTER` variable is a GeoPoint like object which takes in a latitude `lat` and longitude `lng`. All listings around this coordinate with a `RADIUS` would be scraped.

  ```python
  # scrape.py

  CENTER = {"lat": 34.04871368408203, "lng": -118.2420196533203}
  RADIUS = 75
  ```

  For an arbitrary GeoPoint and Radius, at max `10,000` listings can be retrieved.

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

- As of this writing a total of `2,104` listings were successfully scraped around California, LA in a `70mi` radius with center `34.04871368408203, -118.2420196533203`.
- The listings search uses Elasticsearch, therefore a maximum of `10,000` listings can be retrieved.
- Only `User-Agent` has to be set to cloak your bot.
- Rate limiting per IP is implemented. Therefore a service like [Luminati.io](https://luminati.io/) is very essential to burst down requests.
