import requests
import json
import csv
import traceback
import bs4
def get_social_handle(social_link):
    if social_link == None or social_link == "":
        return ""
    social_link = social_link.replace("@", "")
    if social_link[-1] == "/":
        social_link = social_link[:-1]
    return social_link.split("/")[-1]
def get_shop_details(shop):
    URL= "{}/about".format(shop['web_url'])
    headers = {
        'authority': 'weedmaps.com',
        'method': 'GET',
        'scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
    }
    res = requests.get(URL, headers = headers)
    soup = bs4.BeautifulSoup(res.content, 'html.parser')
    scripts = soup.findAll('script')
    data_script = ''
    for script in scripts:
        try:
            if 'NEXT_DATA' in script.string:
                data_script = script.string
        except:
            #traceback.print_exc()
            continue
    data_script = data_script.split('__NEXT_DATA__ = ')[-1].split(';__NEXT_LOADED_PAGES__=')[0]
    data = json.loads(data_script)

    listing = data['props']['pageProps']['storeInitialState']['listing']['listing']
    name = listing['name']
    summary = listing['intro_body']
    rank = '{} ({})'.format(round(listing['rating'],1), listing['reviews_count'])
    phone = listing['phone_number']
    medical = 'medical'
    recreational = 'recreational' if listing['is_recreational'] else ''
    orderonline = 'orderonline' if listing['online_ordering']['enabled_for_pickup'] or listing['online_ordering']['enabled_for_delivery'] else ''
    address1 = '{}, {} {}'.format(   listing['city'],
                                     listing['state'],
                                     listing['zip_code'])
    address2 = listing['address']
    state = listing['state']
    email = listing['email']

    facebook = get_social_handle(listing['social']['facebook_id'])

    if facebook is not "":
        facebook_link = "https://www.facebook.com/{}".format(facebook)
    else:
        facebook_link = ""

    twitter = get_social_handle(listing['social']['twitter_id'])
    if twitter is not "":
        twitter_link = "https://twitter.com/{}".format(twitter)
    else:
        twitter_link = ""

    instagram = get_social_handle(listing['social']['instagram_id'])
    if instagram is not "":
        instagram_link = "https://www.instagram.com/{}".format(instagram)
    else:
        instagram_link = ""

    website = listing['website']
    member_since = listing['member_since']
    medical_licence = []
    adult_use = []
    disributor = []
    micro_bussines = []
    for licence in listing['licenses']:
        if licence["type"] == "Distributor":
            disributor.append(licence['number'])
        if licence["type"] == "Adult-Use Retail":
            adult_use.append(licence['number'])
        if licence["type"] == "Medical Retail":
            medical_licence.append(licence['number'])
        if licence["type"] == "Microbusiness":
            micro_bussines.append(licence['number'])
    medical_licence = ";".join(medical_licence)
    adult_use = ";".join(adult_use)
    disributor = ";".join(disributor)
    micro_bussines = ";".join(micro_bussines)
    return [
        URL, name, summary, rank, phone, medical, recreational, orderonline, address1, address2, state, email, facebook,
        facebook_link, twitter, twitter_link, instagram, instagram_link, website, member_since, medical_licence, adult_use,
        disributor, micro_bussines
    ]



def get_shops(subregion):
    URL = "https://api-g.weedmaps.com/discovery/v1/listings"
    params = [
        {
        'filter[any_retailer_services][]': 'storefront',
        'filter[region_slug[dispensaries]]': subregion['slug'],
        'page_size': '100',
        'size': '100',
        },
        {
        'filter[any_retailer_services][]': 'doctor',
        'filter[region_slug[doctors]]': subregion['slug'],
        'page_size': '100',
        'size': '100',
        },
        {
        'filter[any_retailer_services][]': 'delivery',
        'filter[region_slug[deliveries]]': subregion['slug'],
        'page_size': '100',
        'size': '100',
        }
    ]
    headers = {
        'authority': 'api-g.weedmaps.com',
        'method': 'GET',
        'scheme': 'https',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://weedmaps.com',
        'referer': 'https://weedmaps.com/listings/in/united-states/{}'.format(subregion['slug']),
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36 OPR/56.0.3051.116'
    }
    listings = []
    for param in params:
        res= requests.get(URL, headers = headers, params = param)
        data = json.loads(res.content)
        try:
            for listing in data['data']['listings']:
                listings.append(listing)
        except:
            continue
    return listings
def get_subregions(region):
    URL = "https://api-g.weedmaps.com/wm/v1/regions/{}/subregions".format(region)
    headers = {
        'authority': 'api-g.weedmaps.com',
        'method': 'GET',
        'path': '/wm/v1/regions/{}/subregions'.format(region),
        'scheme': 'https',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://weedmaps.com',
        'referer': 'https://weedmaps.com/listings/in/united-states/{}'.format(region),
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36 OPR/56.0.3051.116'
    }
    res = requests.get(URL, headers = headers)
    data = json.loads(res.content)
    return data['data']['subregions']

region = 'united-states'
states = get_subregions(region)
added_urls = []
print("Region:", region)
with open('{}.csv'.format(region), mode='w', encoding = 'utf-8') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    csv_writer.writerow(['URL','Name', 'Reviews', 'Location', 'Link', 'MenuItems'])
    csv_file_details = open('{}-details.csv'.format(region), mode='w', encoding = 'utf-8')
    csv_writer_details = csv.writer(csv_file_details, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    csv_writer_details.writerow(['URL','Name', 'Summary', 'Rank', 'Phone', 'Medical', 'Recreational',
                                 'Orderonline', 'Address1', 'Address2', 'State', 'Email', 'Facebook', 'Facebook_link',
                                 'Twitter', 'Twitter_link', 'Instagram', 'Instagram_link', 'Website',
                                 'MemberDate', 'Medical-licence', 'Adult-Use Licence', 'Distributor Licence',
                                 'Micobussiness'
                                 ])
    for state in states:
        print("State:", state['slug'])
        subregions = get_subregions(state['slug'])
        for subregion in subregions:
            print("Sub Region:", subregion['slug'])
            try:
                shops = get_shops(subregion)
                for shop in shops:
                    try:
                        shop_detail = [
                            'https://weedmaps.com/listings/in/united-states/{}/{}'.format(region, subregion['slug']),
                            shop['name'],
                            '{} by {} reviews'.format(round(shop['rating'],1), shop['reviews_count']),
                            '{}, {}'.format(shop['city'], shop['state']),
                            shop['web_url'],
                            '{} Menu Items'.format(shop['menu_items_count'])
                        ]
                        if shop['web_url'] not in added_urls:
                            csv_writer.writerow(shop_detail)
                            added_urls.append(shop['web_url'])
                            print("Shop:", shop['name'])
                            details = get_shop_details(shop)
                            csv_writer_details.writerow(details)
                    except:
                        continue
            except:
                continue
print('------------------All Done------------------')