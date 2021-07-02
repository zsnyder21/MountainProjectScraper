-- Table: public.routecomments

-- DROP TABLE public.routecomments;

CREATE TABLE public.routecomments
(
    commentid bigint NOT NULL,
    routeid bigint NOT NULL,
    userid bigint,
    username character varying(128) COLLATE pg_catalog."default",
    commentbody character varying COLLATE pg_catalog."default" NOT NULL,
    commentdate date,
    betavotes integer NOT NULL,
    additionalinfo character varying(128) COLLATE pg_catalog."default",
    CONSTRAINT "PK_RouteComments" PRIMARY KEY (commentid),
    CONSTRAINT "FK_RouteComments_Routes" FOREIGN KEY (routeid)
        REFERENCES public.routes (routeid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE public.routecomments
    OWNER to postgres;
-- Index: IDX_RouteComments_CommentDate

-- DROP INDEX public."IDX_RouteComments_CommentDate";

CREATE INDEX "IDX_RouteComments_CommentDate"
    ON public.routecomments USING btree
    (commentdate ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: IDX_RouteComments_CommentId

-- DROP INDEX public."IDX_RouteComments_CommentId";

CREATE INDEX "IDX_RouteComments_CommentId"
    ON public.routecomments USING btree
    (commentid ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: IDX_RouteComments_RouteId

-- DROP INDEX public."IDX_RouteComments_RouteId";

CREATE INDEX "IDX_RouteComments_RouteId"
    ON public.routecomments USING btree
    (routeid ASC NULLS LAST)
    TABLESPACE pg_default;

ALTER TABLE public.routecomments
    CLUSTER ON "IDX_RouteComments_RouteId";