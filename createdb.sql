create table budget(
    id integer PRIMARY KEY,
    daily_limit integer
);

insert into budget(id, daily_limit) values(1, 0);

create table category(
    name varchar(255) PRIMARY KEY,
    emoji varchar(255),
    aliases text
);

create table expense(
    id integer PRIMARY KEY,
    cash integer,
    category varchar(255),
    created datetime,
    raw_text text
);

insert into category(name, emoji, aliases)
    values
    ("продукты", ":green_apple:", "еда, products"),
    ("кафе", ":fork_and_knife_with_plate:","cafe, ресторан, рест, мак, макдональдс, макдак, kfc, кфс"),
    ("общ. транспорт", ":bus:", "автобус, метро, transport"),
    ("обед", ":pot_of_food:", "столовая, ланч, бизнес-ланч, бизнес ланч, dinner"),
    ("такси", ":taxi:","такса, тэха, taxi"),
    ("телефон", ":mobile_phone:", "связь, phone"),
    ("интернет", ":globe_with_meridians:","инет, inet, internet"),
    ("подписки", ":check_mark:", "подписка, subscriptions"),
    ("прочее", ":money_bag:", "other");
