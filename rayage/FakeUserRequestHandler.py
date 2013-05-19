import constants
import tornado.web
from rayage.database.User import User
from CASVerifiedRequestHandler import CASVerifiedRequestHandler

class FakeUserRequestHandler(CASVerifiedRequestHandler):

    @property
    def permission_level(self):
        """
        Returns the permission_level associated with this connection.
        """
        username = self.get_current_user()
        user = User.get_user(username)
        
        if user is not None:
            return user.permission_level
        return PERMISSION_LEVEL_NONE

    def get(self, username):
        asking_user = self.get_current_user()
        if asking_user is None:
            self.validate_user()
            return
        
        if self.permission_level < constants.PERMISSION_LEVEL_SPOOF:
            raise todo
        user_to_spoof = User.get_user(username)
        if user_to_spoof is None:
            raise todo
        #make sure we're not spoofing as god
        if self.permission_level < user_to_spoof.permission_level:
            raise todo
            
        self.set_secure_cookie("spoofing_user",asking_user)
        self.set_secure_cookie("user", user_to_spoof.username)
        self.redirect(constants.SERVICE_URL, permanent=False)
