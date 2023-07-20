-- Table: public.routeticks

-- DROP TABLE public.routeticks;

CREATE TABLE public.routeticks
(
    tickid bigint NOT NULL,
    routeid bigint NOT NULL,
    userid bigint,
    username character varying(128) COLLATE pg_catalog."default",
    tickdate date,
    tickinfo character varying COLLATE pg_catalog."default",
    url character varying(256) COLLATE pg_catalog."default",
    CONSTRAINT "PK_Ticks" PRIMARY KEY (tickid),
    CONSTRAINT "FK_Ticks_Routes" FOREIGN KEY (routeid)
        REFERENCES public.routes (routeid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE public.routeticks
    OWNER to postgres;

COMMENT ON CONSTRAINT "FK_Ticks_Routes" ON public.routeticks
    IS 'Foreign key constraint from Ticks to Routes';
-- Index: IDX_RouteTicks_RouteId

-- DROP INDEX public."IDX_RouteTicks_RouteId";

CREATE INDEX "IDX_RouteTicks_RouteId"
    ON public.routeticks USING btree
    (routeid ASC NULLS LAST)
    TABLESPACE pg_default;

ALTER TABLE public.routeticks
    CLUSTER ON "IDX_RouteTicks_RouteId";
-- Index: IDX_RouteTicks_TickDate

-- DROP INDEX public."IDX_RouteTicks_TickDate";

CREATE INDEX "IDX_RouteTicks_TickDate"
    ON public.routeticks USING btree
    (tickdate ASC NULLS LAST)
    INCLUDE(tickdate)
    TABLESPACE pg_default;
-- Index: IDX_RouteTicks_TickId

-- DROP INDEX public."IDX_RouteTicks_TickId";

CREATE INDEX "IDX_RouteTicks_TickId"
    ON public.routeticks USING btree
    (tickid ASC NULLS LAST)
    TABLESPACE pg_default;