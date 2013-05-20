import constants
import traceback
import tornado.web
from rayage.database.User import User
from CASVerifiedRequestHandler import CASVerifiedRequestHandler

class SpoofError(ValueError):
    pass

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
        try:
            asking_user = self.get_current_user()
            if asking_user is None:
                self.validate_user()
                return
            
            if self.permission_level < constants.PERMISSION_LEVEL_SPOOF:
                raise SpoofError("You don't have permissions to spoof as another user")
            user_to_spoof = User.get_user(username)
            if user_to_spoof is None:
                raise SpoofError("User {} does not exist.".format(username))
            #make sure we're not spoofing as god
            if self.permission_level < user_to_spoof.permission_level:
                raise SpoofError("You cannot spoof as a user with higher permissions than you. (Then everything WOULD-- nothing wouldn't... what would that even MEAN???)")
                
            self.set_secure_cookie("spoofing_user",asking_user)
            self.set_secure_cookie("user", user_to_spoof.username)
            self.redirect(constants.SERVICE_URL, permanent=False)
        except SpoofError as e:
            username=self.get_current_user()
            user = User.get_user(username)
            self.render("error.html", debug=constants.DEBUG, user=user, constants=constants, traceback=traceback.format_exc())
