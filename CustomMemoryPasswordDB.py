from zope.interface import implements, Interface, Attribute

from twisted.internet import defer
from twisted.python import failure, log
from twisted.cred import error, credentials

class ICredentialsChecker(Interface):
    """
    An object that can check sub-interfaces of ICredentials.
    """

    credentialInterfaces = Attribute(
        'A list of sub-interfaces of ICredentials which specifies which I may check.')


    def requestAvatarId(credentials):
        """
        @param credentials: something which implements one of the interfaces in
        self.credentialInterfaces.

        @return: a Deferred which will fire a string which identifies an
        avatar, an empty tuple to specify an authenticated anonymous user
        (provided as checkers.ANONYMOUS) or fire a Failure(UnauthorizedLogin).
        Alternatively, return the result itself.

        @see: L{twisted.cred.credentials}
        """


class CustomMemoryPwDB:
    implements(ICredentialsChecker)

    credentialInterfaces = (credentials.IUsernamePassword,
                            credentials.IUsernameHashedPassword)
    passwords=[]
    def __init__(self, **users):
        self.users = users
    def addPW(self,pw):
        self.passwords.append(pw)
        
    def addUser(self, username, password):
        self.users[username] = password

    def requestAvatarId(self, credentials):
        print credentials.password
        if credentials.username in self.users and credentials.password in self.passwords:
            return True
        else:
            return defer.fail(error.UnauthorizedLogin()) 
