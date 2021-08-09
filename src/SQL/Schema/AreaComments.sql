-- Table: public.areacomments

-- DROP TABLE public.areacomments;

CREATE TABLE public.areacomments
(
    commentid bigint NOT NULL,
    areaid bigint NOT NULL,
    userid bigint,
    username character varying(128) COLLATE pg_catalog."default",
    commentbody character varying COLLATE pg_catalog."default" NOT NULL,
    commentdate date,
    betavotes integer NOT NULL,
    additionalinfo character varying(128) COLLATE pg_catalog."default",
    CONSTRAINT "PK_AreaComments" PRIMARY KEY (commentid),
    CONSTRAINT "FK_AreaComments_Areas" FOREIGN KEY (areaid)
        REFERENCES public.areas (areaid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE public.areacomments
    OWNER to postgres;

COMMENT ON TABLE public.areacomments
    IS 'Stores comments for areas';

COMMENT ON CONSTRAINT "FK_AreaComments_Areas" ON public.areacomments
    IS 'Foreign key constraint from AreaComments to Areas';
-- Index: IDX_AreaComments_AreaId

-- DROP INDEX public."IDX_AreaComments_AreaId";

CREATE INDEX "IDX_AreaComments_AreaId"
    ON public.areacomments USING btree
    (areaid ASC NULLS LAST)
    TABLESPACE pg_default;

ALTER TABLE public.areacomments
    CLUSTER ON "IDX_AreaComments_AreaId";
-- Index: IDX_AreaComments_CommentDate

-- DROP INDEX public."IDX_AreaComments_CommentDate";

CREATE INDEX "IDX_AreaComments_CommentDate"
    ON public.areacomments USING btree
    (commentdate ASC NULLS LAST)
    TABLESPACE pg_default;