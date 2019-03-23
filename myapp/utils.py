from models import session, User, CatalogItem, Category

# User Helper Functions
def createUser(login_session):
    ''' Create a new user and return user id'''
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    '''get user info from user id'''
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    '''get user Id number from their email address'''
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None
