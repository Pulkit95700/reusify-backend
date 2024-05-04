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
import random
import math

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


def scrap_data_amazon():
    amazon_link = "https://www.amazon.in/recycled-products/s?k=recycled+paper+bags"
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(amazon_link)

    driver.implicitly_wait(10)

    company_name = 'Amazon'
    db = DB.get_db()
    if(db is None):
        return ApiError(500, 'Database Connection Error'), 500
    
    # making company if it does not exist
    company = db.companies.find_one({'name': company_name})

    company_id = None
    
    if not company:
        imgSrc = driver.find_element(By.ID, "nav-logo-sprites").get_attribute("src")
        new_company = Company(company_name, 'Amazon', '9876543210', 'amazon@gmail.com', imgSrc)
        company_id = str(db.companies.insert_one(new_company.to_dict()).inserted_id)
    else:
        company_id = str(company['_id'])
    

    allProductsDiv = driver.find_elements(By.CSS_SELECTOR, 'div.puis-card-container')

    category_name = 'Paper Bags'  
    description = 'Folow thr new habit of taking only paper bags and ignore plastic bags.'
    imageUrl = driver.find_element(By.ID, "nav-logo-sprites").get_attribute("src")

    # checkif category already exists
    category = db.categories.find_one({'category_name': category_name})
    category_id = None
    if not category:
        new_category = Category(category_name, description, imageUrl)
        category_id = str(db.categories.insert_one(new_category.to_dict()).inserted_id)
    else:
        category_id = str(category['_id'])
    
    for i in range(0, len(allProductsDiv)):
        productDiv = allProductsDiv[i]
        productDiv.click()

        driver.implicitly_wait(5)
        # change the tab 
        driver.switch_to.window(driver.window_handles[1])

        driver.implicitly_wait(5)

        product_name = driver.find_element(By.ID, "productTitle").text
        # check if product description is present

        product_description = None
        try:
            product_description = driver.find_element(By.ID, "productDescription")
            product_description = product_description.text
        except:
            product_description = product_name


        price = driver.find_element(By.CSS_SELECTOR, "span.a-price-whole").text
        price = price.replace('.', '')

        print(price)
        mrp = 120 * int(price) / 100

        product_image_urls = []
        allInputButtonElements = driver.find_elements(By.CLASS_NAME, "a-button-input")

        # choose a random number between 3 and 4
        random_number = math.floor(random.random() * 4) + 1 + 4
        for i in range(4, random_number + 1):
            allInputButtonElements[i].click()
            driver.implicitly_wait(5)
            image = driver.find_elements(By.CSS_SELECTOR, "img.a-dynamic-image")
            product_image_urls.append(image[i-4].get_attribute("src"))
        
        print("images fetched")
        # check if product already exists
        product = db.products.find_one({'name': product_name})

        if not product:
            new_product = Product(product_name, int(price), mrp, product_description, company_id, [category_id], product_image_urls)
            db.products.insert_one(new_product.to_dict())
        else:
            print('Product already exists')
        
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        driver.implicitly_wait(5)
        allProductsDiv = driver.find_elements(By.CSS_SELECTOR, 'div.puis-card-container')
        driver.implicitly_wait(5)
