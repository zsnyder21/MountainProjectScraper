-- Table: public.severityreference

-- DROP TABLE public.severityreference;

CREATE TABLE public.severityreference
(
    severityid bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 3764345 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    severity character varying(8) COLLATE pg_catalog."default" NOT NULL,
    severityranking integer NOT NULL,
    CONSTRAINT "PK_SeverityReference_SeverityId" PRIMARY KEY (severityid)
)

TABLESPACE pg_default;

ALTER TABLE public.severityreference
    OWNER to postgres;

COMMENT ON TABLE public.severityreference
    IS 'Hold severity reference data';