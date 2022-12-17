from sqlalchemy import insert, select, create_engine
from table import User as user_table
from table import Address as address_table


# 1.
stmt = insert(user_table).values(name="spongebob", fullname="Spongebob Squarepants")
'''insert().values() : '''
compiled = stmt.compile()
compiled.params

print(stmt)


# 2
engine = create_engine(
    "postgresql://practice:devpassword@localhost:35000/fastapi-practice",
    echo=True,
    future=True,
)

with engine.connect() as conn:
    result = conn.execute(
        insert(user_table),
        [
            {"name": "sandy", "fullname": "Sandy Cheeks"},
            {"name": "patrick", "fullname": "Patrick Star"},
        ],
    )
    conn.commit()

result.inserted_primary_key



# 3
select_stmt = select(user_table.c.id, user_table.c.name + "@aol.com")
# insert from_select
insert_stmt = insert(address_table).from_select(
    ["user_id", "email_address"], select_stmt,
)
print(insert_stmt)
print(insert_stmt.returning(address_table.c.id, address_table.c.email_address)) # insert from select & returning

# insert returning
insert_stmt = insert(address_table).returning(
    address_table.c.id, address_table.c.email_address
)
print(insert_stmt)