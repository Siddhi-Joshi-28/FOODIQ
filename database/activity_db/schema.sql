-- ============================================
-- FOODIQ ACTIVITY DATABASE
-- ============================================


-- ============================================
-- 1. USER SEARCHES
-- ============================================

CREATE TABLE IF NOT EXISTS search_logs (
    search_id SERIAL PRIMARY KEY,
    customer_id INT,
    search_query TEXT NOT NULL,
    search_type VARCHAR(50),
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================
-- 2. FOOD / RESTAURANT VIEWS
-- ============================================

CREATE TABLE IF NOT EXISTS view_logs (
    view_id SERIAL PRIMARY KEY,
    customer_id INT,
    restaurant_id INT,
    food_id INT,
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================
-- 3. CLICKS
-- ============================================

CREATE TABLE IF NOT EXISTS click_logs (
    click_id SERIAL PRIMARY KEY,
    customer_id INT,
    restaurant_id INT,
    food_id INT,
    click_type VARCHAR(50),
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================
-- 4. RECOMMENDATION INTERACTIONS
-- ============================================

CREATE TABLE IF NOT EXISTS recommendation_logs (
    recommendation_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    food_id INT,
    restaurant_id INT,
    recommendation_type VARCHAR(50),
    action VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================
-- 5. USER SESSIONS
-- ============================================

CREATE TABLE IF NOT EXISTS session_logs (
    session_id SERIAL PRIMARY KEY,
    customer_id INT,
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP,
    device VARCHAR(50),
    platform VARCHAR(50)
);


-- ============================================
-- 6. API / SYSTEM ACTIVITY
-- ============================================

CREATE TABLE IF NOT EXISTS api_logs (
    log_id SERIAL PRIMARY KEY,
    endpoint VARCHAR(255),
    method VARCHAR(20),
    status_code INT,
    response_time_ms FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX IF NOT EXISTS idx_search_customer
ON search_logs(customer_id);

CREATE INDEX IF NOT EXISTS idx_search_time
ON search_logs(searched_at);

CREATE INDEX IF NOT EXISTS idx_view_customer
ON view_logs(customer_id);

CREATE INDEX IF NOT EXISTS idx_view_food
ON view_logs(food_id);

CREATE INDEX IF NOT EXISTS idx_click_customer
ON click_logs(customer_id);

CREATE INDEX IF NOT EXISTS idx_recommendation_customer
ON recommendation_logs(customer_id);

CREATE INDEX IF NOT EXISTS idx_session_customer
ON session_logs(customer_id);

CREATE INDEX IF NOT EXISTS idx_api_created
ON api_logs(created_at);