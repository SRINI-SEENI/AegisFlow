-- ============================================================
-- AegisFlow — M1 Schema (Complete DDL for 14 Tables)
-- Applied automatically on first boot via docker-entrypoint-initdb.d
-- ============================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. CUSTOMERS
CREATE TABLE IF NOT EXISTS customers (
    customer_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_ref    VARCHAR(64) UNIQUE NOT NULL,
    full_name       VARCHAR(200) NOT NULL,
    date_of_birth   DATE,
    country_code    CHAR(2) NOT NULL,
    kyc_status      VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (kyc_status IN ('pending','verified','rejected','expired')),
    risk_rating     VARCHAR(10) NOT NULL DEFAULT 'medium'
                    CHECK (risk_rating IN ('low','medium','high')),
    is_pep          BOOLEAN NOT NULL DEFAULT FALSE,
    onboarded_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. ACCOUNTS
CREATE TABLE IF NOT EXISTS accounts (
    account_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id     UUID NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    account_number  VARCHAR(34) UNIQUE NOT NULL,
    account_type    VARCHAR(20) NOT NULL CHECK (account_type IN ('current','savings','card','wallet')),
    currency        CHAR(3) NOT NULL DEFAULT 'INR',
    opened_on       DATE NOT NULL,
    last_active_on  DATE,
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active','dormant','frozen','closed'))
);
CREATE INDEX IF NOT EXISTS idx_accounts_customer ON accounts(customer_id);

-- 3. COUNTERPARTIES
CREATE TABLE IF NOT EXISTS counterparties (
    counterparty_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id      UUID NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    beneficiary_ref VARCHAR(64) NOT NULL,
    beneficiary_name VARCHAR(200),
    country_code    CHAR(2),
    first_seen_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_counterparties_account ON counterparties(account_id);

-- 4. TRANSACTIONS
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id      UUID NOT NULL REFERENCES accounts(account_id),
    counterparty_id UUID REFERENCES counterparties(counterparty_id),
    amount          NUMERIC(14,2) NOT NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'INR',
    channel         VARCHAR(20) NOT NULL,
    ip_address      INET,
    device_fingerprint VARCHAR(255),
    location_country CHAR(2),
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_tx_account_ts ON transactions(account_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_tx_timestamp ON transactions(timestamp);

-- 5. VELOCITY SNAPSHOTS
CREATE TABLE IF NOT EXISTS velocity_snapshots (
    snapshot_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id  UUID NOT NULL UNIQUE REFERENCES transactions(transaction_id),
    tx_count_1h     INT DEFAULT 0,
    tx_count_24h    INT DEFAULT 0,
    tx_sum_24h      NUMERIC(14,2) DEFAULT 0.0,
    unique_counterparties_7d INT DEFAULT 0,
    captured_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. RULE DEFINITIONS
CREATE TABLE IF NOT EXISTS rule_definitions (
    rule_id         VARCHAR(64) PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    action          VARCHAR(10) NOT NULL CHECK (action IN ('approve','review','decline')),
    weight          FLOAT DEFAULT 1.0,
    version         INT NOT NULL DEFAULT 1,
    parameters      JSONB DEFAULT '{}',
    is_active       BOOLEAN DEFAULT TRUE
);

-- 7. RULE HITS
CREATE TABLE IF NOT EXISTS rule_hits (
    hit_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id  UUID NOT NULL REFERENCES transactions(transaction_id),
    rule_id         VARCHAR(64) NOT NULL REFERENCES rule_definitions(rule_id),
    rule_version    INT NOT NULL,
    executed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 8. RISK ASSESSMENTS
CREATE TABLE IF NOT EXISTS risk_assessments (
    assessment_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id  UUID NOT NULL UNIQUE REFERENCES transactions(transaction_id),
    ml_score        FLOAT NOT NULL,
    rules_score     FLOAT NOT NULL,
    blended_score   FLOAT NOT NULL,
    risk_band       VARCHAR(10) NOT NULL CHECK (risk_band IN ('low','medium','high','critical')),
    decision        VARCHAR(10) NOT NULL CHECK (decision IN ('approve','review','decline')),
    reason_codes    JSONB DEFAULT '[]',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 9. ALERTS
CREATE TABLE IF NOT EXISTS alerts (
    alert_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id  UUID NOT NULL REFERENCES transactions(transaction_id),
    alert_type      VARCHAR(100) NOT NULL,
    risk_score      FLOAT NOT NULL,
    status          VARCHAR(20) DEFAULT 'open',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 10. CASES
CREATE TABLE IF NOT EXISTS cases (
    case_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           VARCHAR(255) NOT NULL,
    priority        FLOAT DEFAULT 1.0,
    status          VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open','investigating','pending_review','closed')),
    assigned_to     VARCHAR(255),
    disposition     VARCHAR(20) CHECK (disposition IN ('fraud','not_fraud','sar_filed')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 11. CASE ALERTS
CREATE TABLE IF NOT EXISTS case_alerts (
    case_id         UUID REFERENCES cases(case_id) ON DELETE CASCADE,
    alert_id        UUID REFERENCES alerts(alert_id) ON DELETE CASCADE,
    added_at        TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (case_id, alert_id)
);

-- 12. CASE NOTES
CREATE TABLE IF NOT EXISTS case_notes (
    note_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id         UUID NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
    author          VARCHAR(200) NOT NULL,
    note_text       TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 13. WATCHLIST ENTRIES
CREATE TABLE IF NOT EXISTS watchlist_entries (
    entry_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_name     VARCHAR(200) NOT NULL,
    entity_type     VARCHAR(50) NOT NULL,
    list_name       VARCHAR(100) NOT NULL,
    country_code    CHAR(2),
    added_at        TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_watchlist_name ON watchlist_entries(entity_name);

-- 14. AUDIT LOG
CREATE TABLE IF NOT EXISTS audit_log (
    log_id          BIGSERIAL PRIMARY KEY,
    entity_type     VARCHAR(50) NOT NULL,
    entity_id       VARCHAR(128) NOT NULL,
    action          VARCHAR(50) NOT NULL,
    performed_by    VARCHAR(200) NOT NULL,
    payload         JSONB DEFAULT '{}',
    timestamp       TIMESTAMPTZ DEFAULT NOW()
);
