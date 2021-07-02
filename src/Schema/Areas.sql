-- Table: public.areas

-- DROP TABLE public.areas;

CREATE TABLE public.areas
(
    areaid bigint NOT NULL,
    parentareaid bigint,
    areaname character varying(256) COLLATE pg_catalog."default",
    elevation numeric(14,2),
    elevationunits character varying(2) COLLATE pg_catalog."default",
    latitude numeric(9,4),
    longitude numeric(9,4),
    viewsmonth bigint,
    viewstotal bigint,
    sharedon date,
    overview character varying COLLATE pg_catalog."default",
    description character varying COLLATE pg_catalog."default",
    gettingthere character varying COLLATE pg_catalog."default",
    url character varying(256) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "PK_Areas" PRIMARY KEY (areaid)
)

TABLESPACE pg_default;

ALTER TABLE public.areas
    OWNER to postgres;
-- Index: IDX_Areas_AreaId

-- DROP INDEX public."IDX_Areas_AreaId";

CREATE INDEX "IDX_Areas_AreaId"
    ON public.areas USING btree
    (areaid ASC NULLS LAST)
    TABLESPACE pg_default;

ALTER TABLE public.areas
    CLUSTER ON "IDX_Areas_AreaId";