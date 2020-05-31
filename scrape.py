import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
from math import ceil, sqrt

import coloredlogs
import requests
import xlsxwriter
from jsonschema import validate

coloredlogs.install(
    fmt='%(asctime)s [%(programname)s] %(levelname)s %(message)s')


# define rotating proxies
PROXIES = {
    'http': 'http://lum-customer-hl_58729ae5-zone-static:gksgc5xqf20t@zproxy.lum-superproxy.io:22225',
    'https': 'http://lum-customer-hl_58729ae5-zone-static:gksgc5xqf20t@zproxy.lum-superproxy.io:22225',
}

# define request headers
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0"
}

PAGE_SIZE = 100  # max number of listings per page
MAX_WORKERS = 10  # max number of threads used
MAX_RETRIES = 20  # max number of url fetch attempts

# the method used listing to be aggregated
# can be "region" or "pin"
GATHER_TYPE = "region"

# region to retrieve all coordinates of subregions and listings therein
# can be any region: earth, california, 5-cities, alaska, germany
# used only when GATHER_TYPE is set to "region"
REGION = "california"

# geopoint and fixed radius around which listings will be retrieved
# used only when GATHER_TYPE is set to "pin"
CENTER = {"lat": 34.04871368408203, "lng": -118.2420196533203}  # california
RADIUS = 75  # default radius used by frontend


# expected types of a listing
LISTING_TYPES = {
    "delivery": "deliveries",
    "doctor": "doctors",
    "store": "stores",
    "dispensary": "dispensaries"
}

# expected response of listings on search
LISTINGS_SCHEMA = {
    "type": "object",
    "properties": {
        "meta": {
            "type": "object",
            "properties": {
                "total_listings": {
                    "type": "number"
                }
            }
        },
        "data": {
            "type": "object",
            "properties": {
                "listings": {
                    "type": "array"
                }
            }
        }
    }
}

# default response listings on failure
LISTINGS_DEFAULT = {
    "meta": {"total_listings": 0},
    "data": {"listings": []}
}

# expected response of a listing
LISTING_SCHEMA = {
    "type": "object",
    "properties": {
        "data": {
            "type": "object",
            "properties": {
                "listing": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "number"
                        }
                    }
                }
            }
        }
    }
}

# default response of on failure
LISTING_DEFAULT = {
    "data": {
        "listing": {}
    }
}

# expected response of a region
REGION_SCHEMA = {
    "type": "object",
    "properties": {
        "data": {
            "type": "object",
            "properties": {
                "subregions": {
                    "type": "array"
                }
            }
        }
    }
}

# default response of a region
REGION_DEFAULT = {
    "data": {
        "subregions": []
    }
}

# excel file headers
COL_HEADERS = ('URL', 'About', 'Name', 'Thumbnail', 'Rating',
               'Reviews', 'Type', "Region", "Phone", "Open Hours", "Address", "City", "State", "ZIP Code", "Email", "Website", "Instagram", "Twitter", "Facebook", "Licenses")


# fetch an arbitrary url, check if matches schema and retry if request/schema failed.
def fetch(url, schema, default={}):
    failedAttempts = 0

    while (failedAttempts < MAX_RETRIES):
        try:
            r = requests.get(url, headers=REQUEST_HEADERS, proxies=PROXIES)
        except Exception as e:
            logging.warning('request failed: %s with error: %s' % (url, e))
            failedAttempts += 1
            continue

        if (r.status_code != 200):
            logging.warning('request blocked (%s): %s.' %
                            (r.status_code, url))
            failedAttempts += 1
            continue

        try:
            json = r.json()
            validate(instance=json, schema=schema)
            logging.info('request success (%s): %s' % (r.status_code, url))
            return json
        except Exception:
            logging.warning('bad response (%s): %s. Unexpected response received.' % (
                r.status_code, url))
            failedAttempts += 1
            continue

    if (failedAttempts >= MAX_RETRIES):
        logging.error('request failed: %s, max retries exceeded' % url)

    return default


# fetch one region
def fetchOneRegion(region):
    url = "https://api-g.weedmaps.com/wm/v1/regions/%s/subregions" % region
    return fetch(url, REGION_SCHEMA, REGION_DEFAULT)


# iteratively gather all subarea coordinates from a region
def gatherAllCoordinates(region):
    response = fetchOneRegion(region)
    subregions = response["data"]["subregions"]
    coordinates = []

    if not subregions:
        return coordinates

    # add parent subregion coordinates
    for subregion in subregions:
        coordinates.append(
            {"lat": subregion["latitude"], "lng": subregion["longitude"]})

    # iterate over child subregions and add their coordinates
    with PoolExecutor(max_workers=MAX_WORKERS) as executor:
        for childCoordinates in executor.map(lambda s: gatherAllCoordinates(s["slug"]), subregions):
            coordinates += childCoordinates

    return coordinates


# get listings for a particular page for a given center and radius.
def getOneListings(center, radius, page):
    lat = center['lat']
    lng = center["lng"]
    url = "https://api-g.weedmaps.com/discovery/v1/listings?sort_by=position_distance&filter[bounding_radius]={radius}mi&filter[bounding_latlng]={lat},{lng}&latlng={lat},{lng}&page_size={pageSize}&page={page}".format(
        lat=lat, lng=lng, radius=radius, pageSize=PAGE_SIZE, page=page)

    return fetch(url, LISTINGS_SCHEMA, LISTINGS_DEFAULT)


# get all listings a given center and radius by iterating over available pages
def getAllListings(center, radius):
    response = getOneListings(center, radius, 1)

    total = response["meta"]["total_listings"]
    maxPages = len(range(0, total, PAGE_SIZE))
    listings = response["data"]["listings"]

    logging.info("listings found: %s" % total)

    try:
        with PoolExecutor(max_workers=MAX_WORKERS) as executor:
            for response in executor.map(lambda p: getOneListings(center, radius, p), range(2, maxPages+1)):
                listings += response["data"]["listings"]
        logging.info('fetch all listings: done')
    except Exception as e:
        logging.error('fetch all listings (failed): %s' % e)

    # check data integrity
    if (len(listings) == total):
        logging.info("listings integrity check passed: %s/%s listings received." %
                     (len(listings), total))
    else:
        logging.warning("listings integrity check failed: %s/%s listings received." %
                        (len(listings), total))

    return listings


# get the url of each listing
def gatherListingUrls(listings):
    listingsUrls = []

    # fetch listing urls
    for i in listings:
        listingType = i["type"]
        listingSlug = i["slug"]

        if listingType not in LISTING_TYPES:
            logging.warning("unexpected listing type: %s" % listingType)
            continue

        listingUrl = "https://api-g.weedmaps.com/discovery/v1/listings/%s/%s" % (
            LISTING_TYPES[listingType], listingSlug)

        # filter duplicates
        if listingUrl not in listingsUrls:
            listingsUrls.append(listingUrl)

    return listingsUrls


# get all the info of each listing
def getListing(url):
    response = fetch(url, LISTING_SCHEMA, LISTING_DEFAULT)
    listing = response["data"]["listing"]

    return listing


if __name__ == "__main__":

    # start
    logging.info('bot started')

    # load an excel file
    wb = xlsxwriter.Workbook('dumps/data.xlsx')
    ws = wb.add_worksheet()
    ws.write_row(0, 0, COL_HEADERS)
    rowCount = 0

    # gather listings and urls for given region
    if GATHER_TYPE == "region":
        listings = []
        for center in gatherAllCoordinates(REGION):
            listings += getAllListings(center, RADIUS)
        listingsUrls = gatherListingUrls(listings)

    # gather listings and urls for given center and radius
    if GATHER_TYPE == "pin":
        listings = getAllListings(CENTER, RADIUS)
        listingsUrls = gatherListingUrls(listings)

    # retrieve all listing info
    try:
        with PoolExecutor(max_workers=MAX_WORKERS) as executor:
            for listing in executor.map(getListing, listingsUrls):
                if not listing:
                    continue

                # write listing info to row
                rowCount += 1
                ws.write_row(rowCount, 0, (
                    listing['web_url'],
                    listing['web_url'] + '/about',
                    listing['name'],
                    listing['avatar_image'].get('small_url'),
                    round(listing['rating'], 2),
                    listing['reviews_count'],
                    listing['type'].capitalize(),
                    listing['city'] + ', ' + listing['state'],
                    listing['phone_number'],
                    "%s - %s" % (listing['business_hours'].get('monday').get('open'),
                                 listing['business_hours'].get('monday').get('close')),
                    listing.get('address'),
                    listing['city'],
                    listing['state'],
                    listing['zip_code'],
                    listing['email'],
                    listing['website'],
                    listing['social']['instagram_id'],
                    listing['social']['twitter_id'],
                    listing['social']['facebook_id'],
                    "\n".join(
                        set(map(lambda x: x["type"] + ': ' + x["number"], listing['licenses'])))
                ))
        logging.info('fetch all listing details: done.')
    except Exception as e:
        logging.error('fetch all listing details (failed): %s' % e)

    # save excel data
    wb.close()

    # close bot
    logging.info('bot closed.')
