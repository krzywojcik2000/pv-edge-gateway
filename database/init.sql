-- =====================================================
-- PV EDGE GATEWAY - DATABASE INITIALIZATION SCRIPT
-- =====================================================

-- -----------------------------
-- SCHEMA
-- -----------------------------
CREATE SCHEMA IF NOT EXISTS scada;

-- =====================================================
-- 1. RAW DATA (high-frequency telemetry)
-- =====================================================
CREATE TABLE IF NOT EXISTS scada.raw_measurements (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    farm_id TEXT DEFAULT 'KRK-01',

    temperature INT,
    dc_power INT,
    ac_power INT,
    energy INT,
    alarm INT
);

-- Index for time-based queries (VERY important in SCADA)
CREATE INDEX IF NOT EXISTS idx_raw_ts
ON scada.raw_measurements (ts);


-- =====================================================
-- 2. AGGREGATED DATA (1-minute resolution)
-- =====================================================
CREATE TABLE IF NOT EXISTS scada.aggregate_1min (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    farm_id TEXT DEFAULT 'KRK-01',

    avg_temperature FLOAT,
    avg_dc_power FLOAT,
    avg_ac_power FLOAT,

    energy_sum INT,
    alarm_count INT
);

CREATE INDEX IF NOT EXISTS idx_agg_ts
ON scada.aggregate_1min (ts);


-- =====================================================
-- 3. BUSINESS LAYER (hourly KPI)
-- =====================================================
CREATE TABLE IF NOT EXISTS scada.business_hourly (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    farm_id TEXT DEFAULT 'KRK-01',

    energy_total INT,
    avg_temperature FLOAT,

    alarm_events INT,
    availability FLOAT DEFAULT 100.0
);

CREATE INDEX IF NOT EXISTS idx_business_ts
ON scada.business_hourly (ts);


-- =====================================================
-- 4. ALARMS (event-driven data)
-- =====================================================
CREATE TABLE IF NOT EXISTS scada.alarms (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    farm_id TEXT DEFAULT 'KRK-01',

    alarm_type TEXT,
    message TEXT,
    value INT,
    severity TEXT DEFAULT 'MEDIUM'
);

CREATE INDEX IF NOT EXISTS idx_alarms_ts
ON scada.alarms (ts);


-- =====================================================
-- DONE
-- =====================================================
-- System ready for PV Edge Gateway collector
-- =====================================================