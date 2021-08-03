-- Table: public.difficultyreference

-- DROP TABLE public.difficultyreference;

CREATE TABLE public.difficultyreference
(
    difficultyid bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 645345 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    difficulty character varying(32) COLLATE pg_catalog."default" NOT NULL,
    difficultyranking integer NOT NULL,
    difficultybucket integer NOT NULL,
    difficultybucketname character varying(32) COLLATE pg_catalog."default" NOT NULL,
    ratingsystem character varying(16) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "PK_DifficultyReference" PRIMARY KEY (difficultyid)
)

TABLESPACE pg_default;

ALTER TABLE public.difficultyreference
    OWNER to postgres;

COMMENT ON TABLE public.difficultyreference
    IS 'Table to hold route difficulty reference';
-- Index: IDX_DifficultyReference_Difficulty

-- DROP INDEX public."IDX_DifficultyReference_Difficulty";

CREATE INDEX "IDX_DifficultyReference_Difficulty"
    ON public.difficultyreference USING btree
    (difficulty COLLATE pg_catalog."default" ASC NULLS LAST)
    INCLUDE(difficulty)
    TABLESPACE pg_default;

ALTER TABLE public.difficultyreference
    CLUSTER ON "IDX_DifficultyReference_Difficulty";
-- Index: IDX_DifficultyReference_DifficultyId

-- DROP INDEX public."IDX_DifficultyReference_DifficultyId";

CREATE INDEX "IDX_DifficultyReference_DifficultyId"
    ON public.difficultyreference USING btree
    (difficultyid ASC NULLS LAST)
    INCLUDE(difficultyid)
    TABLESPACE pg_default;
-- Index: IDX_DifficultyReference_DifficultyRanking

-- DROP INDEX public."IDX_DifficultyReference_DifficultyRanking";

CREATE INDEX "IDX_DifficultyReference_DifficultyRanking"
    ON public.difficultyreference USING btree
    (difficultyranking ASC NULLS LAST)
    INCLUDE(difficultyranking)
    TABLESPACE pg_default;