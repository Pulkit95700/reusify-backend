# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from api.db import db as DB
# from api.helpers.ApiError import ApiError
# from api.models.category_model import Category
# from api.models.company_model import Company
# from api.models.product_model import Product
# import os

# # get the website here

# site = "https://saahaszerowaste.com/waste-recycled-products/"

# def scrap_data_saahas():
#     options = webdriver.ChromeOptions()
#     options.add_experimental_option("detach", True)
#     # options.add_argument("--headless")

#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#     driver.get(site)

#     driver.implicitly_wait(10)

#     db = DB.get_db()
#     if(db is None):
#         return ApiError(500, 'Database Connection Error'), 500
    
#     # making company if it does not exist
#     company = db.companies.find_one({'company_name': 'Saahas Zero Waste'})
#     company_id = None
#     if not company:
#         imgSrc = driver.find_element(By.CLASS_NAME, "kode_top_logo").find_element(By.TAG_NAME, "img").get_attribute("src")
#         new_company = Company('Saahas Zero Waste', 'A3, 1st Floor, Cybex Business Centre, 118B,Anna salai, Guindy, Chennai-600032', '9876543210', 'saahas@gmail.com', imgSrc)
#         company_id = str(db.companies.insert_one(new_company.to_dict()).inserted_id)
#     else:
#         company_id = str(company['_id'])

#     allCategoriesDiv = driver.find_element(By.ID, "category-filter-button")

#     allButtons = allCategoriesDiv.find_elements(By.TAG_NAME, "button")

#     for i in range(1, len(allButtons)):
#         button = allButtons[i]
#         button.click()
#         driver.implicitly_wait(15)

#         allProductsLinks = driver.find_elements(By.CLASS_NAME, "woocommerce-LoopProduct-link")

#         # create a category with picture of first product in database
#         category_name = button.text
#         description = button.text
#         imageUrl = allProductsLinks[0].find_element(By.TAG_NAME, "img").get_attribute("src")

#         # checkif category already exists
#         category = db.categories.find_one({'category_name': category_name})
#         category_id = None
#         if not category:
#             new_category = Category(category_name, description, imageUrl)
#             category_id = str(db.categories.insert_one(new_category.to_dict()).inserted_id)
#         else:
#             category_id = str(category['_id'])
        
#         for i in range(0, len(allProductsLinks)):
#             productLink = allProductsLinks[i]
#             productLink.click()
#             driver.implicitly_wait(15)

#             productName = driver.find_element(By.CLASS_NAME, "product_title").text
#             productDescription = driver.find_element(By.CLASS_NAME, "woocommerce-Tabs-panel--description").find_element(By.TAG_NAME, "p").text
#             productPrice = driver.find_element(By.CLASS_NAME, "price").text
#             productPrice = productPrice.replace('₹', '')
#             productPrice = productPrice.replace(',', '')
#             if(productPrice.find('-') != -1):
#                 productPrice = productPrice.split('-')[0]
#             productPrice = productPrice.strip()
#             productPrice = float(productPrice)
#             mrp = productPrice + 10 / 100 * productPrice
#             print(mrp)
#             productImageUrls = []

#             allImagesDiv = driver.find_elements(By.CLASS_NAME, "wvg-gallery-image slick-slide")
#             for image in allImagesDiv:
#                 productImageUrls.append(image.find_element(By.TAG_NAME, "img").get_attribute("src"))
            
#             # check if product already exists
#             product = db.products.find_one({'name': productName})
#             if not product:
#                 new_product = Product(productName, productPrice, mrp, productDescription, company_id, [category_id], productImageUrls)
#                 db.products.insert_one(new_product.to_dict())
#             else:
#                 print('Product already exists')
            
#             driver.back()
#             driver.implicitly_wait(15)

#             allCategoriesDiv = driver.find_element(By.ID, "category-filter-button")
#             allButtons = allCategoriesDiv.find_elements(By.TAG_NAME, "button")

#             button = allButtons[i]
#             button.click()
#             driver.implicitly_wait(25)

#             allProductsLinks = driver.find_elements(By.CLASS_NAME, "woocommerce-LoopProduct-link")