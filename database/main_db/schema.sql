-- ============================================
-- FOODIQ MAIN DATABASE
-- ============================================


-- ============================================
-- CUSTOMERS
-- ============================================

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    age INTEGER,
    city VARCHAR(50),
    email VARCHAR(150) UNIQUE
);


-- ============================================
-- RESTAURANTS
-- ============================================

CREATE TABLE restaurants (
    restaurant_id INTEGER PRIMARY KEY,
    restaurant_name VARCHAR(150) NOT NULL,
    city VARCHAR(50),
    cuisine VARCHAR(50),
    rating DECIMAL(2,1),
    delivery_time_minutes INTEGER,
    is_active BOOLEAN DEFAULT TRUE,

    CONSTRAINT restaurant_rating_check
        CHECK (rating >= 0 AND rating <= 5),

    CONSTRAINT delivery_time_check
        CHECK (delivery_time_minutes > 0)
);


-- ============================================
-- FOODS
-- ============================================

CREATE TABLE foods (
    food_id INTEGER PRIMARY KEY,
    food_name VARCHAR(150) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(10,2),
    rating DECIMAL(2,1),
    is_vegetarian BOOLEAN DEFAULT TRUE,

    CONSTRAINT food_price_check
        CHECK (price > 0),

    CONSTRAINT food_rating_check
        CHECK (rating >= 0 AND rating <= 5)
);


-- ============================================
-- ORDERS
-- ============================================

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,

    customer_id INTEGER NOT NULL,

    restaurant_id INTEGER NOT NULL,

    order_date DATE NOT NULL,

    order_status VARCHAR(30) NOT NULL,

    CONSTRAINT fk_order_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT fk_order_restaurant
        FOREIGN KEY (restaurant_id)
        REFERENCES restaurants(restaurant_id)
);


-- ============================================
-- ORDER ITEMS
-- ============================================

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,

    order_id INTEGER NOT NULL,

    food_id INTEGER NOT NULL,

    quantity INTEGER NOT NULL,

    price DECIMAL(10,2) NOT NULL,

    total_price DECIMAL(10,2) NOT NULL,

    CONSTRAINT fk_order_item_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_order_item_food
        FOREIGN KEY (food_id)
        REFERENCES foods(food_id),

    CONSTRAINT quantity_check
        CHECK (quantity > 0),

    CONSTRAINT item_price_check
        CHECK (price > 0),

    CONSTRAINT total_price_check
        CHECK (total_price > 0)
);


-- ============================================
-- REVIEWS
-- ============================================

CREATE TABLE reviews (
    review_id INTEGER PRIMARY KEY,

    customer_id INTEGER NOT NULL,

    restaurant_id INTEGER NOT NULL,

    rating INTEGER NOT NULL,

    review_text TEXT,

    review_date DATE NOT NULL,

    CONSTRAINT fk_review_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT fk_review_restaurant
        FOREIGN KEY (restaurant_id)
        REFERENCES restaurants(restaurant_id),

    CONSTRAINT review_rating_check
        CHECK (rating >= 1 AND rating <= 5)
);


-- ============================================
-- RATINGS
-- ============================================

CREATE TABLE ratings (
    rating_id SERIAL PRIMARY KEY,

    customer_id INTEGER NOT NULL,

    food_id INTEGER NOT NULL,

    rating INTEGER NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_rating_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT fk_rating_food
        FOREIGN KEY (food_id)
        REFERENCES foods(food_id),

    CONSTRAINT rating_value_check
        CHECK (rating >= 1 AND rating <= 5)
);


-- ============================================
-- DEMAND HISTORY
-- ============================================

CREATE TABLE demand_history (
    demand_id SERIAL PRIMARY KEY,

    food_id INTEGER NOT NULL,

    restaurant_id INTEGER NOT NULL,

    demand_date DATE NOT NULL,

    order_count INTEGER NOT NULL,

    search_count INTEGER DEFAULT 0,

    view_count INTEGER DEFAULT 0,

    CONSTRAINT fk_demand_food
        FOREIGN KEY (food_id)
        REFERENCES foods(food_id),

    CONSTRAINT fk_demand_restaurant
        FOREIGN KEY (restaurant_id)
        REFERENCES restaurants(restaurant_id),

    CONSTRAINT demand_order_check
        CHECK (order_count >= 0)
);


-- ============================================
-- REVENUE HISTORY
-- ============================================

CREATE TABLE revenue_history (
    revenue_id SERIAL PRIMARY KEY,

    restaurant_id INTEGER NOT NULL,

    revenue_date DATE NOT NULL,

    total_orders INTEGER NOT NULL,

    total_revenue DECIMAL(12,2) NOT NULL,

    CONSTRAINT fk_revenue_restaurant
        FOREIGN KEY (restaurant_id)
        REFERENCES restaurants(restaurant_id),

    CONSTRAINT revenue_order_check
        CHECK (total_orders >= 0),

    CONSTRAINT revenue_amount_check
        CHECK (total_revenue >= 0)
);