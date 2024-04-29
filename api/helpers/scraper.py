from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from api.db import db as DB
from api.helpers.ApiError import ApiError
from api.models.category_model import Category
from api.models.company_model import Company
from api.models.product_model import Product
import os

# get the website here
def scrap_data_saahas():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    # options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://saahaszerowaste.com/waste-recycled-products/")

    driver.implicitly_wait(10)

    db = DB.get_db()
    if(db is None):
        return ApiError(500, 'Database Connection Error'), 500
    
    # making company if it does not exist
    company = db.companies.find_one({'company_name': 'Saahas Zero Waste'})
    company_id = None
    if not company:
        imgSrc = driver.find_element(By.CLASS_NAME, "kode_top_logo").find_element(By.TAG_NAME, "img").get_attribute("src")
        new_company = Company('Saahas Zero Waste', 'A3, 1st Floor, Cybex Business Centre, 118B,Anna salai, Guindy, Chennai-600032', '9876543210', 'saahas@gmail.com', imgSrc)
        company_id = str(db.companies.insert_one(new_company.to_dict()).inserted_id)
    else:
        company_id = str(company['_id'])

    allCategoriesDiv = driver.find_element(By.ID, "category-filter-button")

    allButtons = allCategoriesDiv.find_elements(By.TAG_NAME, "button")

    for i in range(1, len(allButtons)):
        button = allButtons[i]
        button.click()
        driver.implicitly_wait(15)

        allProductsLinks = driver.find_elements(By.CLASS_NAME, "woocommerce-LoopProduct-link")

        # create a category with picture of first product in database
        category_name = button.text
        description = button.text
        imageUrl = allProductsLinks[0].find_element(By.TAG_NAME, "img").get_attribute("src")

        # checkif category already exists
        category = db.categories.find_one({'category_name': category_name})
        category_id = None
        if not category:
            new_category = Category(category_name, description, imageUrl)
            category_id = str(db.categories.insert_one(new_category.to_dict()).inserted_id)
        else:
            category_id = str(category['_id'])
        
        for i in range(0, len(allProductsLinks)):
            productLink = allProductsLinks[i]
            productLink.click()
            driver.implicitly_wait(5)
            productName = driver.find_element(By.CLASS_NAME, "product_title").text
            productDescription = driver.find_element(By.CLASS_NAME, "woocommerce-Tabs-panel--description").find_element(By.TAG_NAME, "p").text
            productPrice = driver.find_element(By.CLASS_NAME, "price").text
            productPrice = productPrice.replace('₹', '')
            productPrice = productPrice.replace(',', '')
            if(productPrice.find('–') != -1):
                productPrice = productPrice.split('–')[0]
            productPrice = productPrice.strip()
            productPrice = float(productPrice)
            mrp = productPrice + 10 / 100 * productPrice
            print(mrp)
            productImageUrls = []
            
            driver.implicitly_wait(15)
            # wait for 15 seconds here
            
            productImageUrls.append(driver.find_element(By.CSS_SELECTOR, "img.zoomImg").get_attribute("src"))
            
            # check if product already exists
            product = db.products.find_one({'name': productName})
            if not product:
                new_product = Product(productName, productPrice, mrp, productDescription, company_id, [category_id], productImageUrls)
                db.products.insert_one(new_product.to_dict())
            else:
                print('Product already exists')
            
            driver.back()
            driver.implicitly_wait(15)

            allCategoriesDiv = driver.find_element(By.ID, "category-filter-button")
            allButtons = allCategoriesDiv.find_elements(By.TAG_NAME, "button")

            button = allButtons[i]
            button.click()
            driver.implicitly_wait(25)

            allProductsLinks = driver.find_elements(By.CLASS_NAME, "woocommerce-LoopProduct-link")


# for etsy

categories = [
    {'name': "recyclable plastic", 'url': 'https://images.pexels.com/photos/802221/pexels-photo-802221.jpeg?auto=compress&cs=tinysrgb&w=600'},
{'name': "recyclable paper", 'url': 'https://images.pexels.com/photos/19868406/pexels-photo-19868406/free-photo-of-coffee-mug-and-cookies-on-paper-and-feathers.jpeg?auto=compress&cs=tinysrgb&w=600'},
   {'name': "Reusable glass", 'url': 'https://images.pexels.com/photos/3735200/pexels-photo-3735200.jpeg?auto=compress&cs=tinysrgb&w=600'},
    {'name': "recyclable metal", 'url': 'https://images.pexels.com/photos/4195603/pexels-photo-4195603.jpeg?auto=compress&cs=tinysrgb&w=600'},
    {'name': "Recycled fabric", 'url': 'https://images.pexels.com/photos/6044417/pexels-photo-6044417.jpeg?auto=compress&cs=tinysrgb&w=600'},
]

# def scrap_data_etsy():
#     options = webdriver.ChromeOptions()
#     options.add_experimental_option("detach", True)
#     # options.add_argument("--headless")

#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#     driver.get("https://www.etsy.com/")

#     driver.implicitly_wait(15)

#     db = DB.get_db()
#     if(db is None):
#         return ApiError(500, 'Database Connection Error'), 500
    
#     # making company if it does not exist
#     company = db.companies.find_one({'company_name': 'Etsy'})
#     company_id = None
#     if not company:
#         imgSrc = "https://cdn.worldvectorlogo.com/logos/etsy-2.svg"
#         new_company = Company('Etsy', '55 Washington St, Suite 512, Brooklyn, NY 11201', '9876543210', 'etsy@gmail.com', '7188557955', imgSrc)
#         company_id = str(db.companies.insert_one(new_company.to_dict()).inserted_id)
#     else:
#         company_id = str(company['_id'])
    
#     for category in categories:
#         # checkif category already exists
#         category_name = category['name']
#         category = db.categories.find_one({'category_name': category_name})
#         category_id = None

#         print(category)
#         if not category:
#             new_category = Category(category_name, category_name, category['url'])
#             category_id = str(db.categories.insert_one(new_category.to_dict()).inserted_id)
#         else:
#             category_id = str(category['_id'])
        
#         inputElement = driver.find_element(By.ID, "global-enhancements-search-query")
#         print("innput")
#         # clear the input field
#         inputElement.clear()
#         inputElement.send_keys(category_name)  

#         searchButton = driver.find_element(By.CLASS_NAME, "wt-input-btn-group__btn global-enhancements-search-input-btn-group__btn")
#         searchButton.click()

#         driver.implicitly_wait(15)

#         olElement = driver.find_element(By.CLASS_NAME, "wt-grid wt-grid--block wt-pl-xs-0 tab-reorder-container")

#         allH3Elements = olElement.find_elements(By.CLASS_NAME, "wt-text-caption v2-listing-card__title wt-text-truncate")

#         for i in range(0, 11):
#             h3Element = allH3Elements[i]
#             h3Element.click()
#             driver.implicitly_wait(15)

#             # changing the window
#             driver.switch_to.window(driver.window_handles[1])

#             driver.implicitly_wait(5)

#             productName = driver.find_element(By.CLASS_NAME, "wt-text-body-01 wt-line-height-tight wt-break-word wt-mt-xs-1").text
#             productDescription = driver.find_element(By.ID, "wt-content-toggle-product-details-read-more").find_element(By.TAG_NAME, "p").text
#             # product description to maximum length of 500
#             productDescription = productDescription[:500]
#             productPrice = driver.find_element(By.CLASS_NAME, "wt-text-title-larger wt-mr-xs-1").text
#             productPrice = productPrice.replace('₹', '')
#             # remove all instead of numbers
#             productPrice = productPrice.replace(',', '')
#             for ch in productPrice:
#                 if not ch.isdigit():
#                     productPrice = productPrice.replace(ch, '')
#             productPrice = productPrice.strip()
#             productPrice = float(productPrice)

#             productImageUrls = []

#             ulElement = driver.find_element(By.CLASS_NAME, "wt-list-unstyled  wt-position-relative carousel-pane-list")
#             allImagesEle = ulElement.find_elements(By.TAG_NAME, "img")

#             for image in allImagesEle:
#                 productImageUrls.append(image.get_attribute("src"))
            
#             mrp = productPrice + 0.3 * productPrice
#             # check if product already exists
#             product = db.products.find({'name': productName})
#             if not product:
#                 new_product = Product(productName, productPrice, mrp, productDescription, company_id, [category_id], productImageUrls)
#                 db.products.insert_one(new_product.to_dict())
#             else:
#                 print('Product already exists')
            
#             driver.close()
#             driver.switch_to.window(driver.window_handles[0])
#             driver.implicitly_wait(15)