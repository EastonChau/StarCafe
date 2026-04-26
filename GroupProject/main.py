#   Student name: Chau Yat Tung
#   Student ID: 3036327923
#   Course code and assignment title
from pyscript import when, fetch, document, window
import json
from datetime import datetime



# base URL using firebase
BASE_URL = "https://group-project-355f4-default-rtdb.asia-southeast1.firebasedatabase.app/user"

cart = {}

#user class
class UserProfile:
    def __init__(self, name=None, uid=None, balance=0):
        self.user_name = name
        self.user_id = uid
        self.user_balance = balance 

    def get_summary(self):
        return f"Account ID: {self.user_id} | Name: {self.user_name} | Balance: ${self.user_balance}"



class Purchasable:
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price
        self.tax = self.price * 0.01
    def get_summary(self):
        return f"ID: {self.id} | Name: {self.name} | Tax: ${self.tax:.2f}"


#item class
class FoodItem(Purchasable):
    def __init__(self, id, name, price):
        super().__init__(id, name, price)

    def get_summary(self):
        return f"ID: {self.id} | Name: {self.name} | Price: ${self.price}"

class Service(Purchasable):
    def __init__(self, id, name, price, duration):
        super().__init__(id, name, price)
        self.duration = duration

class Souvenir(Purchasable):
    def __init__(self, id, name, price, weight):
        super().__init__(id, name, price)
        self.weight = weight



user_login = UserProfile()

#switch between login and signup
@when("click", "#link-to-signup")
def show_signup(event):
    document.getElementById("login-form").style.display = "none"
    document.getElementById("signup-form").style.display = "block"
    document.getElementById("hint").style.display = "none"
@when("click", "#link-to-login")
def show_login(event):
    document.getElementById("signup-form").style.display = "none"
    document.getElementById("login-form").style.display = "block"
    document.getElementById("hint").style.display = "none"


@when("click", "#login-btn")
async def login(event):
    ac_input = document.getElementById("name").value
    pw_input = document.getElementById("login-password").value
    await login_reused(ac_input, pw_input)

async def login_reused(name, password):
    loader = document.getElementById("loading-card")
    loader.style.display = "flex"
    try:
        ac_input = name
        pw_input = password
        
        users = await fetch(f"{BASE_URL}.json").json() or {}  
        #Firebase Json Structure
        #user:
        #{
        #"id1": {
        #    "ac": "Tom",
        #    "balance": 2,
        #    "pass": "123"
        #},
        #"id2": {
        #    "ac": "Tim",
        #    "balance": 188,
        #   "pass": "123"     }}

        target_user_data = None
        for user_id, user_data in users.items():
            if (user_data) and (str(user_data.get("ac")) == ac_input) and (str(user_data.get("pass")) == pw_input):
                
                global user_login
                user_login.user_name = str(user_data.get("ac")) #write the login info for later use     
                user_login.user_id = user_id
                user_login.user_balance = user_data.get("balance")
                
                print(f"Logged in! ID: {user_login.user_id}")
                target_user_data = user_data
                document.getElementById("menu-title").innerText = f"Welcome, {target_user_data.get('ac')}!"
                document.getElementById("balance-display").innerText = f"Balance: ${target_user_data.get('balance', 0)}"
                document.getElementById("auth-card").style.display = "none"
                document.getElementById("dashboard-section").style.display = "block"
                await load_food_menu()
                document.getElementById("open-sidebar-btn").style.display = "flex"
                break
            else: 
                msg = document.getElementById("hint")
                msg.innerText = "Invalid credentials!"
                msg.style.color = "red"
                msg.style.display = "flex"
    finally:
        loader.style.display = "none"
############################# above checked by Easton ##############################################################################################################################################################################################

@when("click", "#signup-btn")
async def signup(event):
    nm_input = document.getElementById("signup-name").value
    pw_input = document.getElementById("signup-password").value
    msg = document.getElementById("hint")
    msg.style.display = 'none'

    if not nm_input or not pw_input:
        msg.innerText = "Please fill in all fields!"
        msg.style.color = "red"
        msg.style.display = 'flex'
        return

    response = await fetch(f"{BASE_URL}.json").json()
    users = response if response else {}

    # case insensitive
    if any(userValue and (str(userValue.get("ac")).lower() == nm_input.lower()) for userValue in users.values()):
        msg.innerText = f"'{nm_input}' is already taken!"
        msg.style.color = "red"
        msg.style.display = 'flex'
        return 
    
    # make new id
    ID_nums_in_DB = [int(ke.replace("id", "")) for ke in users.keys() if ke.startswith("id")]
    new_ID_num = max(ID_nums_in_DB) + 1 if ID_nums_in_DB else 1
    new_ID = f"id{new_ID_num}"
    
    global user_login
    user_login = UserProfile(nm_input, new_ID, 1000)

    new_user = {
        "ac": nm_input, 
        "balance": 1000, #every new user gets 1000
        "pass": pw_input
    }
    await fetch(f"{BASE_URL}/{new_ID}.json", method="PUT", body=json.dumps(new_user))
    
    # show welcome messages
    document.getElementById("signup-form").style.display = "none"
    document.getElementById("welcome-card").style.display = "flex"
############################# above checked by Easton ############################################################################################################################################################################################## 

@when("click", "#close-welcome") #Following clicking x on the welcome message and signup, it gets to the main menu page
async def close_welcome_modal(event): 
    document.getElementById("welcome-card").style.display = "none"
    document.getElementById("auth-card").style.display = "none"
    document.getElementById("dashboard-section").style.display = "block"
    document.getElementById("open-sidebar-btn").style.display = "flex"
    await load_food_menu()

async def load_food_menu():
    loader = document.getElementById("loading-card")
    loader.style.display = "flex"
    try:
        food_url = "https://group-project-355f4-default-rtdb.asia-southeast1.firebasedatabase.app/food.json"
        response = await fetch(food_url).json()
        food_list_div = document.getElementById("food-list")
        food_list_div.innerHTML = ""
        global user_login
        if response:
            document.getElementById("menu-title").innerText = f"Welcome, {user_login.user_name}!"

            for key, item in response.items():
                foodInstance = FoodItem(key, item['name'], int(item['price']))
                img_url = item['img']
                
                food_card = f"""
                <div class="food-item">
                    <img src="{img_url}" alt="{foodInstance.name}">

                    <p style="margin: 0;">{foodInstance.name}</p>
                    <p id="display-price-{foodInstance.id}" style="margin: 0;">${foodInstance.price}</p>

                    <div class="user-input">
                        <div class="size-toggle">
                            <label class="switch">
                                <input type="checkbox" id="size-{foodInstance.id}" onchange="update_cart_size('{foodInstance.id}', {foodInstance.price})">
                                <span class="slider circular-toggle"></span>
                            </label>
                        </div>

                        <div class="qty-controls">
                            <button class="qty-btn" onclick="change_qty('{foodInstance.id}', -1, '{foodInstance.name}', {foodInstance.price}, '{img_url}')">-</button>
                            <span id="qty-{foodInstance.id}" class="qty">0</span>
                            <button class="qty-btn" onclick="change_qty('{foodInstance.id}', 1, '{foodInstance.name}', {foodInstance.price}, '{img_url}')">+</button>
                        </div>
                    </div>
                </div>
                """
                food_list_div.innerHTML += food_card
    
    
    finally:
        loader.style.display = "none"



############################# above checked by Easton ##############################################################################################################################################################################################

#after clicking - or + button, it makes changes to the cart and ui
def change_qty(food_id, delta, name, base_price, img):
    qty_shown = document.getElementById(f"qty-{food_id}")
    new_qty = int(qty_shown.innerText) + delta
    img_url = img

    if new_qty >= 0:
        qty_shown.innerText = str(new_qty)
        
        size = "L" if document.getElementById(f"size-{food_id}").checked else "M"
        
        # with $6 extra if Large
        actual_price = base_price + 6 if size == "L" else base_price

        if new_qty > 0:
            cart[food_id] = {
                "name": name,
                "qty": new_qty,
                "size": size,
                "price": actual_price,
                "total": actual_price * new_qty,
                "img": img_url
            }
        else:
            cart.pop(food_id, None)
        
    print(f"Cart: {cart}")
window.change_qty = change_qty #this button triggers the above


def update_cart_size(food_id, base_price):
    size = "L" if document.getElementById(f"size-{food_id}").checked else "M"
    actual_price = base_price + 6 if size == "L" else base_price
    
    price_shown = document.getElementById(f"display-price-{food_id}")
    if price_shown:
        price_shown.innerText = f"${actual_price}"
    #update cart
    if food_id in cart:
        qty = cart[food_id]["qty"]
        cart[food_id]["size"] = size
        cart[food_id]["price"] = actual_price
        cart[food_id]["total"] = actual_price * qty
    
    print(f"Cart: {cart}")
window.update_cart_size = update_cart_size #this button triggers the above

############################# above checked by Easton ##############################################################################################################################################################################################

### Below is sidebar menu ###
@when("click", "#open-sidebar-btn")
def open_sidebar(event):
    document.getElementById("sidebar").classList.add("active")

@when("click", "#close-sidebar")
def close_sidebar(event):
    document.getElementById("sidebar").classList.remove("active")

@when("click", "#logout-btn")
def logout(event):
    window.location.reload()

@when("click", "#menu-btn")
async def menu(event):
    loader = document.getElementById("loading-card")
    loader.style.display = "flex"
    global cart
    try:
        document.getElementById("auth-card").style.display = "none"
        document.getElementById("cart-container").style.display = "none"
        document.getElementById("profile-card").style.display = "none"
        document.getElementById("dashboard-section").style.display = "block"
        await load_food_menu()
        load_cart2()
    finally:
        loader.style.display = "none"

def load_cart2(): #this handles memory when users get from other pages to cart
    global cart
    for key, item in cart.items():
        qty_label = document.getElementById(f"qty-{key}")
        if qty_label:
            qty_label.innerText = str(item['qty'])
        
        size = item["size"] #change size toggle appearance
        checkbox = document.getElementById(f"size-{key}")
        checkbox.checked = True if size == "L" else False 

        if checkbox.checked:
            price = item["price"]
            priceTag = document.getElementById(f"display-price-{key}")
            priceTag.innerText  = f'${price}'
            
############################# above checked by Easton ##############################################################################################################################################################################################         

#get to cart when the sidebar button is clicked
@when("click", "#cart-btn")
def opencart(event):
    document.getElementById("dashboard-section").style.display = "none"
    document.getElementById("contact-card").style.display = "none"
    document.getElementById("profile-card").style.display = "none"
    document.getElementById("cart-container").style.display = "block"
    
    cart_list_div = document.getElementById("cart-food-container")
    cart_list_div.innerHTML = "" 
    
    total_raw = 0
    drink_count = 0
    food_count = 0

    btn = document.getElementById("purchase-btn")
    btn.disabled = True

    drink_ids = ["food1", "food2", "food3", "food4", "food5", "food6", "food7"]

    if cart == {}:
        cart_list_div.innerHTML = "(Empty)"
    else:
        for key, item in cart.items():
            
            total_raw += item['total']
            
            if key in drink_ids:
                drink_count += item['qty']
            else:
                food_count += item['qty']
            
            food_img = item.get('img', '')

            checked = "checked" if item['size'] == "L" else ""
            base_price = item['price'] if item['size'] == "M" else (item['price']-6)

            food_card = f"""
            <div class="food-item">
                <img src="{food_img}" alt="{item['name']}">
                <p style="margin: 0;">{item['name']}</p>
                <p id="cart-display-price-{key}" style="margin: 0;">${item['price']}</p>
                
                <div class="user-input">
                    
                    <div class="size-toggle">
                        <label class="switch">
                            <input type="checkbox" id="cart-size-{key}" {checked} onchange="update_cart_size_in_cart('{key}', {base_price})">
                            <span class="slider circular-toggle"></span>
                        </label>
                    </div>

                
                    <div class="qty-controls">
                        <button class="qty-btn" onclick="change_qty_in_cart('{key}', -1, '{item['name']}', {base_price}, '{food_img}')">-</button>
                        <span id="cart-qty-{key}" class="qty">{item['qty']}</span>
                        <button class="qty-btn" onclick="change_qty_in_cart('{key}', 1, '{item['name']}', {base_price}, '{food_img}')">+</button>
                    </div>
                
                </div>
            </div>
            """
            cart_list_div.innerHTML += food_card       
        btn.disabled = False

    no_combos = min(food_count, drink_count)
    total_discount = no_combos * 5 #discount per combo is $5
    final_total = max(0, total_raw - total_discount)
    
    discount_msg = f"Combo x{no_combos} Discount: ${total_discount}" if no_combos > 0 else f"Combo x{0} Discount: ${0}"
    document.getElementById("combo-discount-text").innerText = discount_msg
    document.getElementById("total-price-display").innerText = f"Total Price: ${final_total}"

############################# above checked by Easton ##############################################################################################################################################################################################

def change_qty_in_cart(food_id, delta, name, price,img):
    qty_element = document.getElementById(f"cart-qty-{food_id}")
    current_qty = int(qty_element.innerText)
    new_qty = current_qty + delta
    img_url = img
    base_price = price

    if new_qty >= 0:
        qty_element.innerText = str(new_qty)
        size = "L" if document.getElementById(f"cart-size-{food_id}").checked else "M"
        actual_price = base_price + 6 if size == "L" else base_price

        if new_qty > 0:
            cart[food_id] = {
                "name": name,
                "qty": new_qty,
                "size": size,
                "price": actual_price,
                "total": actual_price * new_qty,
                "img": img_url
            }
        else:
            cart.pop(food_id, None)
        
        print(f"Cart: {cart}")
        opencart(None)


def update_cart_size_in_cart(food_id,  base_price):
    is_L = document.getElementById(f"cart-size-{food_id}").checked
    size = "L" if is_L else "M"
    actual_price = base_price + 6 if is_L else base_price
    
    price_display = document.getElementById(f"display-price-{food_id}")
    if price_display:
        price_display.innerText = f"${actual_price}"
    
    # Update the global cart
    if food_id in cart:
        qty = cart[food_id]["qty"]
        cart[food_id]["size"] = size
        cart[food_id]["price"] = actual_price
        cart[food_id]["total"] = actual_price * qty

    print(f"Cart: {cart}")
    opencart(None)

window.change_qty_in_cart = change_qty_in_cart
window.update_cart_size_in_cart = update_cart_size_in_cart

############################# above checked by Easton ##############################################################################################################################################################################################

@when("click", "#purchase-btn")
def go2Contact(event):
    document.getElementById("cart-container").style.display = "none"
    document.getElementById("contact-card").style.display = "block"
        

async def load_profile():
    document.getElementById("cart-container").style.display = "none"
    document.getElementById("contact-card").style.display = "none"
    document.getElementById("dashboard-section").style.display = "none"
    document.getElementById("profile-card").style.display = "block"
    order_container = document.getElementById("order-list")

    loader = document.getElementById("loading-card")
    loader.style.display = "flex"

    global user_login
    balance = user_login.user_balance
    userName = user_login.user_name
    userId = user_login.user_id

    head = document.getElementById("profile-head")
    head.innerHTML = f"""
    <h2>Account Name: {userName}</h2>
    <h2>Balance: ${balance}</h2>
    """
    try: 
        purchase_url = "https://group-project-355f4-default-rtdb.asia-southeast1.firebasedatabase.app/purchase.json"
        response = await fetch(purchase_url)
        all_orders = await response.json()
        
        order_container.innerHTML = ""

        for p_id, data in all_orders.items():
            if str(data.get("id")) == str(userId):
                
                items_html = ""
                for item_key, item in data.get("items", {}).items():
                    items_html += f"""
                    <tr>
                        <td>{item['name']} ({item['size']})</td>
                        <td>{item['qty']}</td>
                        <td>${item['price']}</td>
                        <td>${item['total']}</td>
                    </tr>
                    """

                order_card = f"""
                <div class="order-card">
                    <div class="order-header">
                        <p>Date & Time : {data.get('when')}</p>
                        <p>Name : {data.get('name')}</p>
                        <p>Contact : {data.get('contact')}</p>
                    </div>

                    
                    <table class="order-items-table">
                        <thead>
                            <tr>
                                <th>Item</th>
                                <th>Qty</th>
                                <th>Price</th>
                                <th>Subtotal</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    <div class="order-summary">
                        <div>Discount: -${data.get('discount', 0)}</div>
                        <div class="total-payable">Total Payable: ${data.get('finalpri')}</div>
                    </div>
                </div>
                """
                order_container.innerHTML += order_card
    finally:
        loader.style.display = "none"

############################# above checked by Easton ##############################################################################################################################################################################################

@when("click", "#profile-btn")
async def profilePage(event):
    await load_profile()

@when("click", "#contact-btn")
async def inputContact(event):
    msg = document.getElementById("contact-message")
    msg.style.display = "none"
    global user_login, cart
    balance = user_login.user_balance
    userName = user_login.user_name
    userId = user_login.user_id

    total_raw = 0
    drink_count = 0
    food_count = 0

    drink_ids = ["food1", "food2", "food3", "food4", "food5", "food6", "food7"]

    for key, item in cart.items():
        total_raw += item['total']

        if key in drink_ids:
            drink_count += item['qty']
        else:
            food_count += item['qty']

    no_combos = min(food_count, drink_count)
    discount = no_combos * 5
    final_total = total_raw - discount

    user_input = document.getElementById("contact-input").value.strip()
    
    if len(user_input) == 8 and user_input.isdigit():    
        if balance < final_total:  
            msg.innerText = "Insufficient balance!"
            msg.style.color = "red"
            msg.style.display = "flex"
            return

        contact = user_input

        purchase_url = "https://group-project-355f4-default-rtdb.asia-southeast1.firebasedatabase.app/purchase.json"
        p_res = await fetch(purchase_url)
        p_data = await p_res.json()
        
        next_id = "p1"
        if p_data:
            existing_nums = [int(k.replace('p', '')) for k in p_data.keys() if k.startswith('p')]
            if existing_nums:
                next_id = f"p{max(existing_nums) + 1}"

        new_record = {
            "when": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "name": userName,
            "id": userId,
            "contact": contact,
            "items": cart.copy(),
            "discount": discount,
            "finalpri": final_total
        }

        save_purchase_url = f"https://group-project-355f4-default-rtdb.asia-southeast1.firebasedatabase.app/purchase/{next_id}.json"
        await fetch(save_purchase_url, method="PUT", body=json.dumps(new_record))

        balance -= final_total
        user_update_url = f"https://group-project-355f4-default-rtdb.asia-southeast1.firebasedatabase.app/user/{userId}.json"
        await fetch(user_update_url, method="PATCH", body=json.dumps({"balance": balance}))
        user_login.user_balance = balance
        cart.clear()
        await load_profile()

    else:
        msg.style.display = "flex"
        msg.innerText = "Please enter 8 digits!"


document.getElementById("loading-indic").style.display = "none"
document.getElementById("main-card").style.display = "block"