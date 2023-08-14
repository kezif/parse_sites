import re
import modal
#import requests
import time
import pickle

image = modal.Image.debian_slim(python_version="3.10").pip_install(["aiohttp", "requests"]) 
'''.run_commands(
    "apt-get install -y software-properties-common",
    "apt-add-repository non-free",
    "apt-add-repository contrib",
    "apt-get update",
    "pip install playwright==1.30.0",
    "playwright install-deps chromium",
    "playwright install chromium",
)'''

stub = modal.Stub(name="market-scraper")



@stub.function(image=image, retries=5)
async def get_item_names(start: int):
    import aiohttp

    base_url  = 'https://steamcommunity.com/market/search/render/?search_descriptions=0&sort_column=default&sort_dir=desc&appid=730&norender=1&count=50&start={}'

    t1 = time.time()
    async with aiohttp.ClientSession() as session:

        async with session.get(base_url.format(start)) as resp:
            resp = await resp.json()
            
    if resp['total_count'] == 0:
        raise ValueError(f'Empty responce {start}')
    
    names = [item['hash_name'] for item in resp['results']]
    print(f'Done parsing {start} chunk in {time.time()-t1}s')
    return names

@stub.function(image=image, retries=5)
async def get_item_price_history(start: int):
    import aiohttp

    base_url  = 'https://steamcommunity.com/market/search/render/?search_descriptions=0&sort_column=default&sort_dir=desc&appid=730&norender=1&count=50&start={}'

    t1 = time.time()
    async with aiohttp.ClientSession() as session:

        async with session.get(base_url.format(start)) as resp:
            resp = await resp.json()
            
    if resp['total_count'] == 0:
        raise ValueError(f'Empty responce {start}')
    
    names = [item['hash_name'] for item in resp['results']]
    print(f'Done parsing {start} chunk in {time.time()-t1}s')
    return names





@stub.local_entrypoint()
def main():
   

    t0 = time.time()
    items_names = []
    for items in get_item_names.map(range(0,20556, 50)):  # 20556 is hardcoded value. Its total number of items. You could get it by launching function once and u'll get total count
        items_names.extend(items)

  
    
    print(f'Done exctracting item names in {time.time()-t0}s')  
    print(items_names[:20])
    t0 = time.time()
    print(f'Done pasing item names in {time.time()-t0}s')  
    with open('item_names.pkl', 'wb') as file:
        pickle.dump(items_names, file)

    


