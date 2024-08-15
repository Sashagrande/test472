--migrate:up
CREATE TABLE public.points (
	symbol_id serial4 NOT NULL,
	rate float8 NOT NULL,
	created timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX created_idx ON public.points USING btree (created DESC NULLS LAST);
CREATE INDEX symbol_id_idx ON public.points USING hash (symbol_id);

CREATE TABLE public.symbols (
	id serial NOT NULL,
	symbol varchar NOT NULL,
	CONSTRAINT points_pk PRIMARY KEY (id),
	CONSTRAINT points_unique UNIQUE (symbol)
);

INSERT INTO public.symbols (id, symbol) VALUES(1, 'EURUSD');
INSERT INTO public.symbols (id, symbol) VALUES(2, 'USDJPY');
INSERT INTO public.symbols (id, symbol) VALUES(3, 'GBPUSD');
INSERT INTO public.symbols (id, symbol) VALUES(4, 'AUDUSD');
INSERT INTO public.symbols (id, symbol) VALUES(5, 'USDCAD');

--migrate:down
DROP TABLE public.points;
DROP TABLE public.symbols;
