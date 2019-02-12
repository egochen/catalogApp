from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, CatalogItem, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Chenyang Wu", email="chenyarron@gmail.com")
session.add(User1)
session.commit()

# Catalog for Tennis
category1 = Category(user_id=1, name="Tennis")

session.add(category1)
session.commit()

catalogItem2 = CatalogItem(user_id=1, title="Racket", description="The hitting tool", category=category1)

session.add(catalogItem2)
session.commit()


catalogItem1 = CatalogItem(user_id=1, title="Tennis ball", description="The yellow ball",category=category1)

session.add(catalogItem1)
session.commit()

# more categories
cat = Category(user_id=1, name="Soccer")

session.add(cat)
session.commit()

catalogItem1 = CatalogItem(user_id=1, title="Jersey",
                           description="Lorem ipsum dolor sit amet",category=cat)
session.add(catalogItem1)
session.commit()

catalogItem1 = CatalogItem(user_id=1, title="Shinguards",
                           description="consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur",category=cat)
session.add(catalogItem1)
session.commit()


# more categories
cat = Category(user_id=1, name="Baseball")

session.add(cat)
session.commit()

# more categories
cat = Category(user_id=1, name="Basketball")

session.add(cat)
session.commit()

# more categories
cat = Category(user_id=1, name="Snowboarding")

session.add(cat)
session.commit()

# more categories
cat = Category(user_id=1, name="Frisbee")

session.add(cat)
session.commit()

# more categories
cat = Category(user_id=1, name="Rock Climbing")

session.add(cat)
session.commit()

# more categories
cat = Category(user_id=1, name="Skating")

session.add(cat)
session.commit()

# more categories
cat = Category(user_id=1, name="Hockey")

session.add(cat)
session.commit()

