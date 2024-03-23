DO $$
DECLARE
    r record;
BEGIN
    FOR r IN
        SELECT c.relname AS seqname, t.relname AS tablename, a.attname AS columnname
        FROM pg_class c
        JOIN pg_depend d ON d.objid = c.oid
        JOIN pg_class t ON d.refobjid = t.oid
        JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = d.refobjsubid
        WHERE c.relkind = 'S' AND d.deptype = 'a'
    LOOP
        EXECUTE 'SELECT setval(' || quote_literal(r.seqname) || ', COALESCE(MAX(' || quote_ident(r.columnname) || '), 0) + 1) FROM ' || quote_ident(r.tablename) || ';';
    END LOOP;
END $$;
