

DROP TABLE IF EXISTS patent_info  CASCADE;;
DROP TABLE IF EXISTS company_info  CASCADE;;

CREATE TABLE public.company_info
(
    company_name varchar(128) NOT NULL,
    address varchar(128),
    address2 varchar(128),
    city varchar(64),
    category_name varchar(64),
    url varchar(256),
    hiring BOOLEAN,
    jobs_url varchar(256),
    why_nyc varchar(2048),
    email varchar(1024)
);

ALTER TABLE company_info ADD CONSTRAINT C_PRIMARY PRIMARY KEY (company_name); 

commit;

CREATE TABLE public.patent_info
(
     company_name varchar(128) NOT NULL,
     title varchar(256),
     patent_inventor varchar(1024),
     reference varchar(1024)
);

alter table patent_info
add constraint fk_product foreign key (company_name)
references company_info(company_name);

commit;
