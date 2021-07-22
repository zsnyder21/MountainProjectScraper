-- Table: public.routeratings

-- DROP TABLE public.routeratings;

CREATE TABLE public.routeratings
(
    ratingid bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 632653867 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    routeid bigint NOT NULL,
    userid bigint,
    username character varying(128) COLLATE pg_catalog."default",
    rating integer NOT NULL,
    "URL" character varying(256) COLLATE pg_catalog."default",
    CONSTRAINT "PK_RouteRatings" PRIMARY KEY (ratingid),
    CONSTRAINT "FK_RouteRatings_Routes" FOREIGN KEY (routeid)
        REFERENCES public.routes (routeid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE public.routeratings
    OWNER to postgres;

COMMENT ON TABLE public.routeratings
    IS 'Table to hold user ratings of routes';

COMMENT ON CONSTRAINT "FK_RouteRatings_Routes" ON public.routeratings
    IS 'Foreign key constraint from RouteRatings to Routes';
-- Index: IDX_RouteRatings_RatingId

-- DROP INDEX public."IDX_RouteRatings_RatingId";

CREATE INDEX "IDX_RouteRatings_RatingId"
    ON public.routeratings USING btree
    (ratingid ASC NULLS LAST)
    INCLUDE(ratingid)
    TABLESPACE pg_default;
-- Index: IDX_RouteRatings_RouteId

-- DROP INDEX public."IDX_RouteRatings_RouteId";

CREATE INDEX "IDX_RouteRatings_RouteId"
    ON public.routeratings USING btree
    (routeid ASC NULLS LAST)
    INCLUDE(routeid)
    TABLESPACE pg_default;

ALTER TABLE public.routeratings
    CLUSTER ON "IDX_RouteRatings_RouteId";
-- Index: IDX_RouteRatings_UserId

-- DROP INDEX public."IDX_RouteRatings_UserId";

CREATE INDEX "IDX_RouteRatings_UserId"
    ON public.routeratings USING btree
    (userid ASC NULLS LAST)
    INCLUDE(userid)
    TABLESPACE pg_default;