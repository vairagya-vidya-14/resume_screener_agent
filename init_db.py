import os
import sys
import pymysql
from dotenv import load_dotenv
from flask import Flask
from models import db, MenuItem, Reservation, ContactMessage, Review, CustomDrink, Offer, GalleryItem, Order

load_dotenv()

MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root')
MYSQL_DB = os.getenv('MYSQL_DB', 'viyora_cafe')

def ensure_mysql_database():
    """Ensure the MySQL database exists on the server, create if missing."""
    print(f"Connecting to MySQL server at {MYSQL_HOST}:{MYSQL_PORT}...")
    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            connect_timeout=3
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print(f"[OK] MySQL database '{MYSQL_DB}' is ready!")
        conn.close()
        return f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    except Exception as e:
        print(f"[NOTE] MySQL Connection notice: {e}")
        print("Using database backend 'sqlite:///viyora_cafe.db'")
        return "sqlite:///viyora_cafe.db"

def seed_database(app):
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"[NOTE] Table check: {e}")

        # Check if already seeded
        if MenuItem.query.count() > 0:
            print("[OK] Database already populated with menu items!")
            return

        print("[INFO] Seeding 58 Menu Items into Database...")

        items = [
            # 12 COFFEES
            # Classic Coffees
            (1, "Espresso", "coffee", "☕ Classic Coffees", "Rich and bold single espresso shot brewed from organic dark roast beans.", 3.50, "Bestseller", "images/coffee_1.jpg"),
            (2, "Double Espresso", "coffee", "☕ Classic Coffees", "Intense double shot of dark roasted espresso with golden crema.", 4.20, "Strong", "images/coffee_2.jpg"),
            (3, "Americano", "coffee", "☕ Classic Coffees", "Espresso shots diluted with hot water for a rich, smooth flavor.", 3.90, None, "images/coffee_3.jpg"),
            # Cold Coffees
            (4, "Iced Americano", "coffee", "🧊 Cold Coffees", "Crisp double espresso over cold filtered water and ice cubes.", 4.25, "Chilled", "images/coffee_4.jpg"),
            (5, "Iced Latte", "coffee", "🧊 Cold Coffees", "Smooth espresso with cold whole milk served over crushed ice.", 4.60, "Popular", "images/coffee_5.jpg"),
            (6, "Iced Mocha", "coffee", "🧊 Cold Coffees", "Belgian dark chocolate syrup with cold espresso & milk over ice.", 4.90, None, "images/coffee_6.jpg"),
            (7, "Cold Coffee", "coffee", "🧊 Cold Coffees", "Blended creamy cold coffee topped with cocoa powder & chocolate syrup.", 4.50, "Refresh", "images/coffee_7.jpg"),
            (8, "Cold Brew", "coffee", "🧊 Cold Coffees", "Slow-steeped 18-hour cold brew with natural sweetness & smooth finish.", 4.80, None, "images/coffee_8.jpg"),
            # Signature Coffees
            (9, "Caramel Cloud Coffee", "coffee", "✨ Signature Coffees", "Velvety steamed espresso topped with cloud cream foam & salted caramel drizzle.", 5.50, "Signature", "images/coffee_9.jpg"),
            (10, "Vanilla Dream Latte", "coffee", "✨ Signature Coffees", "French Madagascan vanilla bean infusion with silky textured microfoam.", 5.25, "House Special", "images/coffee_10.jpg"),
            (11, "Hazelnut Velvet", "coffee", "✨ Signature Coffees", "Roasted hazelnut syrup blended with dark espresso & steamed milk foam.", 5.40, None, "images/coffee_11.jpg"),
            (12, "Mocha Bliss", "coffee", "✨ Signature Coffees", "Triple chocolate mocha with whipped cream topping & dark chocolate shavings.", 5.60, "Decadent", "images/coffee_12.jpg"),

            # 29 FOOD ITEMS
            # Burgers & Sandwiches
            (13, "Classic Veg Burger", "food", "🍔 Burgers & Sandwiches", "Crispy garden veggie patty with fresh lettuce, tomato & house herb mayo on toasted brioche.", 7.50, "Bestseller", "images/food_16.jpg"),
            (14, "Crispy Chicken Burger", "food", "🍔 Burgers & Sandwiches", "Golden seasoned crispy chicken breast with spicy aioli & crunchy pickles.", 8.90, "Popular", "images/food_17.jpg"),
            (15, "Paneer Burger", "food", "🍔 Burgers & Sandwiches", "Spiced grilled cottage cheese slab with mint chutney spread & crunchy onions.", 8.20, None, "images/food_18.jpg"),
            (16, "Grilled Cheese Sandwich", "food", "🍔 Burgers & Sandwiches", "Melted triple-cheese blend of aged cheddar, mozzarella & parmesan on buttered sourdough.", 6.80, None, "images/food_19.jpg"),
            (17, "Club Sandwich", "food", "🍔 Burgers & Sandwiches", "Triple-decker toasted sandwich with roasted veggies, turkey, bacon & honey mustard.", 9.20, None, "images/food_20.jpg"),
            # Quick Bites
            (18, "Margherita Pizza", "food", "🍕 Quick Bites & Pizzas", "Hand-tossed crust topped with San Marzano tomato sauce, fresh mozzarella & basil.", 10.50, "Classic", "images/food_21.jpg"),
            (19, "Veggie Pizza", "food", "🍕 Quick Bites & Pizzas", "Loaded with bell peppers, sweet corn, mushrooms, black olives & extra cheese.", 11.80, None, "images/food_22.jpg"),
            (20, "Chicken Pizza", "food", "🍕 Quick Bites & Pizzas", "Herbed chicken chunks, red onions, BBQ sauce glaze & melted mozzarella.", 12.90, None, "images/food_23.jpg"),
            (21, "Garlic Bread", "food", "🍕 Quick Bites & Pizzas", "Toasted baguette slices infused with garlic herb butter & roasted parsley.", 4.50, None, "images/food_24.jpg"),
            (22, "Cheese Garlic Bread", "food", "🍕 Quick Bites & Pizzas", "Golden garlic bread smothered in melted mozzarella & oregano seasoning.", 5.50, "Bestseller", "images/food_25.jpg"),
            # Pasta & Mains
            (23, "White Sauce Pasta", "food", "🍝 Pasta & Mains", "Penne pasta tossed in rich parmesan cream sauce with sautéed mushrooms.", 9.80, "Chef Special", "images/food_26.jpg"),
            (24, "Arrabbiata Pasta", "food", "🍝 Pasta & Mains", "Spicy red tomato basil sauce with chili flakes, garlic & parmesan shavings.", 9.50, None, "images/food_27.jpg"),
            (25, "Creamy Alfredo Pasta", "food", "🍝 Pasta & Mains", "Fettuccine pasta in heavy cream, butter & freshly grated aged parmesan cheese.", 10.20, None, "images/food_28.jpg"),
            # Wraps & Rolls
            (26, "Paneer Wrap", "food", "🌯 Wraps & Rolls", "Spiced cottage cheese cubes wrapped in tortilla with mint mayonnaise & onion rings.", 7.80, None, "images/food_29.jpg"),
            (27, "Veggie Wrap", "food", "🌯 Wraps & Rolls", "Fresh avocado, spinach, bell peppers & chickpea hummus in a whole wheat tortilla.", 7.20, None, "images/food_30.jpg"),
            (28, "Chicken Shawarma Roll", "food", "🌯 Wraps & Rolls", "Slow-roasted marinated chicken in flatbread with garlic toum sauce & pickles.", 8.50, "Favorite", "images/food_31.jpg"),
            # Breakfast
            (29, "Masala Omelette", "food", "🍳 Breakfast Specials", "Spiced three-egg omelette with diced onions, tomatoes, green chilies & butter toast.", 6.50, None, "images/food_32.jpg"),
            (30, "Cheese Omelette", "food", "🍳 Breakfast Specials", "Fluffy organic egg omelette stuffed with melted sharp cheddar cheese.", 6.90, None, "images/food_33.jpg"),
            (31, "Golden French Toast", "food", "🍳 Breakfast Specials", "Thick brioche slices dipped in vanilla cinnamon batter, served with maple syrup.", 7.40, "Sweet", "images/food_34.jpg"),
            # Cafe Snacks
            (32, "Crispy Veg Samosa", "food", "🥐 Cafe Snacks & Bakery", "Golden fried pastry pocket stuffed with spiced potato & green peas mixture.", 3.50, "Crispy", "images/food_35.jpg"),
            (33, "Veg Puff", "food", "🥐 Cafe Snacks & Bakery", "Flaky puff pastry filled with seasoned mixed vegetables & aromatic herbs.", 3.25, None, "images/food_36.jpg"),
            (34, "Chicken Puff", "food", "🥐 Cafe Snacks & Bakery", "Layered golden pastry filled with savory minced chicken & spices.", 3.95, None, "images/food_37.jpg"),
            (35, "Paneer Puff", "food", "🥐 Cafe Snacks & Bakery", "Crispy puff pastry stuffed with spicy cottage cheese filling.", 3.75, None, "images/food_38.jpg"),
            # Light & Healthy
            (36, "Garden Veg Sandwich", "food", "🥗 Light & Healthy", "Whole wheat bread with cucumber, tomato, lettuce & mint spread.", 5.80, None, "images/food_39.jpg"),
            (37, "Grilled Chicken Salad", "food", "🥗 Light & Healthy", "Juicy grilled chicken breast, mixed greens, avocado & lemon vinaigrette.", 9.80, "Healthy", "images/food_40.jpg"),
            (38, "Classic Caesar Salad", "food", "🥗 Light & Healthy", "Crisp romaine lettuce, garlic croutons, parmesan cheese & Caesar dressing.", 8.90, None, "images/food_41.jpg"),
            (39, "Fresh Seasonal Fruit Bowl", "food", "🥗 Light & Healthy", "Assorted fresh strawberries, blueberries, kiwi, mango & honey mint syrup.", 6.50, "Fresh", "images/food_42.jpg"),
            (40, "Artisanal Avocado Toast", "food", "🥗 Light & Healthy", "Toasted sourdough topped with smashed avocado, poached organic egg & chili flakes.", 8.50, "Signature", "images/food_43.jpg"),
            (41, "Corn & Cheese Salad", "food", "🥗 Light & Healthy", "Sweet corn kernels, bell peppers, feta cheese & herb lime dressing.", 6.90, None, "images/food_44.jpg"),

            # 17 DESSERT ITEMS
            # Cakes & Pastries
            (42, "Chocolate Truffle Cake", "desserts", "🍰 Cakes & Pastries", "Rich Belgian dark chocolate truffle cake topped with cocoa dusting & fresh berries.", 6.50, "Bestseller", "images/dessert_31.jpg"),
            (43, "Red Velvet Cake", "desserts", "🍰 Cakes & Pastries", "Moist red velvet sponge layers filled with silky smooth vanilla cream cheese frosting.", 6.25, "Popular", "images/dessert_32.jpg"),
            (44, "Blueberry Cheesecake", "desserts", "🍰 Cakes & Pastries", "New York baked cream cheesecake topped with wild blueberry compote.", 6.80, None, "images/dessert_33.jpg"),
            (45, "Lotus Biscoff Cheesecake", "desserts", "🍰 Cakes & Pastries", "Creamy Biscoff cookie butter cheesecake with crushed Biscoff biscuit crust.", 7.20, "Signature", "images/dessert_34.jpg"),
            (46, "Chocolate Brownie", "desserts", "🍰 Cakes & Pastries", "Fudgy dark chocolate brownie baked with real cocoa chunks.", 4.50, None, "images/dessert_35.jpg"),
            (47, "Fudge Brownie with Ice Cream", "desserts", "🍰 Cakes & Pastries", "Warm fudge brownie topped with a scoop of Madagascar vanilla ice cream & hot chocolate drizzle.", 5.90, "Favorite", "images/dessert_36.jpg"),
            # Cookies & Bites
            (48, "Chocolate Chip Cookies", "desserts", "🍪 Cookies & Bites", "Classic warm butter cookies packed with melted milk chocolate chips.", 3.50, "Fresh Baked", "images/dessert_37.jpg"),
            (49, "Double Chocolate Cookies", "desserts", "🍪 Cookies & Bites", "Dark cocoa cookie dough loaded with white & dark chocolate chunks.", 3.75, None, "images/dessert_38.jpg"),
            (50, "Red Velvet Cookies", "desserts", "🍪 Cookies & Bites", "Chewy red velvet cookies swirled with sweet cream cheese morsels.", 3.90, None, "images/dessert_39.jpg"),
            (51, "Brookies", "desserts", "🍪 Cookies & Bites", "Ultimate hybrid fusion: Half fudgy brownie and half chocolate chip cookie.", 4.25, "Special", "images/dessert_40.jpg"),
            (52, "Oatmeal Raisin Cookies", "desserts", "🍪 Cookies & Bites", "Whole grain oats baked with Ceylon cinnamon & sweet sun-dried raisins.", 3.60, None, "images/dessert_41.jpg"),
            # Cold Desserts
            (53, "Mango Cream Cup", "desserts", "🍨 Cold Desserts", "Alphonso mango pulp layered with chilled vanilla cream & graham crumbles.", 4.95, "Refreshing", "images/dessert_42.jpg"),
            (54, "Classic Ice Cream Scoop", "desserts", "🍨 Cold Desserts", "Scoop of artisan gelato (Choice of Vanilla Bean, Dark Chocolate, or Pistachio).", 3.50, None, "images/dessert_43.jpg"),
            (55, "Tiramisu Cup", "desserts", "🍨 Cold Desserts", "Espresso-soaked ladyfingers in a cup with mascarpone mousse & cocoa dust.", 5.25, "Classic", "images/dessert_44.jpg"),
            # Cafe Specials
            (56, "Nutella Pancakes", "desserts", "🥞 Cafe Specials", "Fluffy buttermilk pancakes stacked with warm Nutella spread & sliced banana.", 6.90, "House Special", "images/dessert_45.jpg"),
            (57, "Biscoff Pancakes", "desserts", "🥞 Cafe Specials", "Golden pancake stack drizzled with melted Biscoff cookie butter & crumbles.", 7.10, None, "images/dessert_46.jpg"),
            (58, "Chocolate Waffles", "desserts", "🥞 Cafe Specials", "Belgian waffle baked with cocoa batter, served with maple syrup & dark chocolate chips.", 6.80, "Crispy", "images/dessert_47.jpg")
        ]

        for num, name, cat, subcat, desc, price, badge, img in items:
            m = MenuItem(
                item_number=num,
                name=name,
                category=cat,
                subcategory=subcat,
                description=desc,
                price=price,
                badge=badge,
                image_url=img
            )
            db.session.add(m)

        # Seed Offers
        offers = [
            Offer(title="Morning Coffee Rush", code="VIYORA20", discount="20% OFF", description="Get 20% off all Classic & Cold Coffees between 8 AM and 11 AM daily.", badge="Hot Offer"),
            Offer(title="Combo Feast Deal", code="FEAST30", discount="30% OFF", description="Buy any Burger or Pasta and get a Coffee or Dessert at 30% off.", badge="Popular"),
            Offer(title="Weekend Dessert Bonanza", code="SWEET50", discount="Buy 1 Get 1", description="Buy any Signature Cheesecake and get a Classic Ice Cream Scoop free.", badge="Weekend Special")
        ]
        for o in offers:
            db.session.add(o)

        # Seed Reviews
        reviews = [
            Review(author_name="Sophia Martinez", rating=5, comment="Viyora Café serves the smoothest Caramel Cloud Coffee I've ever had! Beautiful ambience and super friendly staff.", date_posted="2 days ago", avatar="👩‍💼"),
            Review(author_name="David Miller", rating=5, comment="The White Sauce Pasta and Crispy Chicken Burger are top tier. Always my go-to spot for remote work & coffee.", date_posted="1 week ago", avatar="👨‍💻"),
            Review(author_name="Emma Watson", rating=5, comment="Lotus Biscoff Cheesecake is pure heaven! Generous portions and incredible coffee quality.", date_posted="2 weeks ago", avatar="👩‍🎨")
        ]
        for r in reviews:
            db.session.add(r)

        db.session.commit()
        print("[SUCCESS] Database initialized & seeded with 58 menu items, offers, and reviews!")

if __name__ == '__main__':
    db_uri = ensure_mysql_database()
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    seed_database(app)
