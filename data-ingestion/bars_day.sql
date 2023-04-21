-- Table: public.bars_day

-- DROP TABLE IF EXISTS public.bars_day;

CREATE TABLE IF NOT EXISTS public.bars_day
(
    "date" date NOT NULL,
    "symbol" character varying(10) COLLATE pg_catalog."default" NOT NULL,
    "open" real NOT NULL,
    "close" real NOT NULL,
    "high" real NOT NULL,
    "low" real NOT NULL,
    "volume" integer NOT NULL
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.bars_day
    OWNER to postgres;