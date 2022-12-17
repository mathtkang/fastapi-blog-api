from sqlalchemy import insert, select, create_engine
from table import User
from table import Address
from sqlalchemy.orm import Session


engine = create_engine(
    "postgresql://practice:devpassword@localhost:35000/fastapi-practice",
    echo=True,
    future=True,
)

# user = User(
#     name="Spongebob",
#     fullname="Spongebob Squarepants",
# )


stmt = select(User).where(User.name == "Spongebob")
# stmt = stmt.where(User.fullname == "Spongebob Squarepants")
# stmt = stmt.order_by(User.id.desc())


with Session(engine) as session:
    # session.add(user)
    # session.commit()

    user: User | None = session.execute(
        # select(User)
        # .where(User.name == "Spongebob")
        stmt
    ).scalar_one_or_none()
    print(user)

    # Update
    user.fullname = "Spongebob Circlepants"
    session.add(user)

    # Delete
    session.delete(user)

    # session.flush()  # push to database no commit
    session.commit()  # push to database with commit

    print(user)  # implicit select only insert or update



# (User(id=1, name='Spongebob', fullname='Spongebob Squarepants'),)
# User(id=1, name='Spongebob', fullname='Spongebob Squarepants')



# alembic
# Command
# - upgrade {target_migration_commit} git pull
# - downgrade {target_migration_commit} git reset or revert
# - revision git commit

# - stamp
# - merge