-- Creates the table that stores daily spot prices.
-- Primary key (period, series) means one price per date per series,
-- so reloading data can never create duplicates.

CREATE TABLE IF NOT EXISTS spot_prices (
    period             DATE          NOT NULL,
    series             TEXT          NOT NULL,
    series_description TEXT,
    value              NUMERIC(10,2),
    units              TEXT,
    loaded_at          TIMESTAMPTZ   DEFAULT now(),
    PRIMARY KEY (period, series)
);