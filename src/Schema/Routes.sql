-- Table: public.routes

-- DROP TABLE public.routes;

CREATE TABLE public.routes
(
    routeid bigint NOT NULL,
    areaid bigint NOT NULL,
    routename character varying(256) COLLATE pg_catalog."default" NOT NULL,
    difficulty_yds character varying(8) COLLATE pg_catalog."default",
    difficulty_french character varying(8) COLLATE pg_catalog."default",
    difficulty_adl character varying(32) COLLATE pg_catalog."default",
    severity character varying(8) COLLATE pg_catalog."default",
    type character varying(64) COLLATE pg_catalog."default",
    height numeric(14,2),
    heightunits character varying(2) COLLATE pg_catalog."default",
    pitches integer,
    grade integer,
    description character varying COLLATE pg_catalog."default",
    location character varying COLLATE pg_catalog."default",
    protection character varying COLLATE pg_catalog."default",
    firstascent character varying(256) COLLATE pg_catalog."default",
    firstascentyear integer,
    firstfreeascent character varying(256) COLLATE pg_catalog."default",
    firstfreeascentyear integer,
    averagerating integer,
    votecount integer,
    url character varying(256) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "PK_Routes" PRIMARY KEY (routeid),
    CONSTRAINT "FK_Routes_Areas" FOREIGN KEY (areaid)
        REFERENCES public.areas (areaid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE public.routes
    OWNER to postgres;

COMMENT ON CONSTRAINT "FK_Routes_Areas" ON public.routes
    IS 'Foriegn key constraint between Routes and Areas';
-- Index: IDX_Routes_AreaId

-- DROP INDEX public."IDX_Routes_AreaId";

CREATE INDEX "IDX_Routes_AreaId"
    ON public.routes USING btree
    (areaid ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: IDX_Routes_RouteId

-- DROP INDEX public."IDX_Routes_RouteId";

CREATE INDEX "IDX_Routes_RouteId"
    ON public.routes USING btree
    (routeid ASC NULLS LAST)
    TABLESPACE pg_default;

ALTER TABLE public.routes
    CLUSTER ON "IDX_Routes_RouteId";