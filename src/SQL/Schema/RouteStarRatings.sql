-- Table: public.routestarratings

-- DROP TABLE public.routestarratings;

CREATE TABLE public.routestarratings
(
    ratingid bigint NOT NULL,
    routeid bigint NOT NULL,
    userid bigint,
    username character varying(128) COLLATE pg_catalog."default",
    rating integer NOT NULL,
    url character varying(256) COLLATE pg_catalog."default",
    CONSTRAINT "PK_RouteStarRatings" PRIMARY KEY (ratingid),
    CONSTRAINT "FK_RouteStarRatings_Routes" FOREIGN KEY (routeid)
        REFERENCES public.routes (routeid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE public.routestarratings
    OWNER to postgres;

COMMENT ON TABLE public.routestarratings
    IS 'Table to hold user star ratings of routes';

COMMENT ON CONSTRAINT "FK_RouteStarRatings_Routes" ON public.routestarratings
    IS 'Foreign key constraint from routestarratings to Routes';
-- Index: IDX_routestarratings_RatingId

-- DROP INDEX public."IDX_routestarratings_RatingId";

CREATE INDEX "IDX_routestarratings_RatingId"
    ON public.routestarratings USING btree
    (ratingid ASC NULLS LAST)
    INCLUDE(ratingid)
    TABLESPACE pg_default;
-- Index: IDX_routestarratings_RouteId

-- DROP INDEX public."IDX_routestarratings_RouteId";

CREATE INDEX "IDX_RouteStarRatings_RouteId"
    ON public.routestarratings USING btree
    (routeid ASC NULLS LAST)
    INCLUDE(routeid)
    TABLESPACE pg_default;

ALTER TABLE public.routestarratings
    CLUSTER ON "IDX_RouteStarRatings_RouteId";
-- Index: IDX_routestarratings_UserId

-- DROP INDEX public."IDX_routestarratings_UserId";

CREATE INDEX "IDX_RouteStarRatings_UserId"
    ON public.routestarratings USING btree
    (userid ASC NULLS LAST)
    INCLUDE(userid)
    TABLESPACE pg_default;