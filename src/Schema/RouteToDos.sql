-- Table: public.routetodos

-- DROP TABLE public.routetodos;

CREATE TABLE public.routetodos
(
    todoid bigint NOT NULL,
    routeid bigint NOT NULL,
    userid bigint,
    username character varying(128) COLLATE pg_catalog."default",
    "URL" character varying(256) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "PK_RouteToDos_ToDoId" PRIMARY KEY (todoid),
    CONSTRAINT "FK_RouteToDos_Routes" FOREIGN KEY (routeid)
        REFERENCES public.routes (routeid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE public.routetodos
    OWNER to postgres;

COMMENT ON TABLE public.routetodos
    IS 'Stores user To-Dos for routes';

COMMENT ON CONSTRAINT "FK_RouteToDos_Routes" ON public.routetodos
    IS 'Foreign key constraint from RouteToDos to Rotues';
-- Index: IDX_RouteToDos_RouteId

-- DROP INDEX public."IDX_RouteToDos_RouteId";

CREATE INDEX "IDX_RouteToDos_RouteId"
    ON public.routetodos USING btree
    (routeid ASC NULLS LAST)
    INCLUDE(routeid)
    TABLESPACE pg_default;

ALTER TABLE public.routetodos
    CLUSTER ON "IDX_RouteToDos_RouteId";
-- Index: IDX_RouteToDos_ToDoId

-- DROP INDEX public."IDX_RouteToDos_ToDoId";

CREATE INDEX "IDX_RouteToDos_ToDoId"
    ON public.routetodos USING btree
    (todoid ASC NULLS LAST)
    INCLUDE(todoid)
    TABLESPACE pg_default;
-- Index: IDX_RouteToDos_UserId

-- DROP INDEX public."IDX_RouteToDos_UserId";

CREATE INDEX "IDX_RouteToDos_UserId"
    ON public.routetodos USING btree
    (userid ASC NULLS LAST)
    INCLUDE(userid)
    TABLESPACE pg_default;