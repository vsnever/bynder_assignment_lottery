
# Lottery exceptions
class LotteryAlreadyExists(Exception):
    pass

class LotteryInvalidClosureDate(Exception):
    pass

class LotteryNotFound(Exception):
    pass

class LotteryAlreadyClosed(Exception):
    pass

class LotteryNotClosed(Exception):
    pass

class LotteryNoWinnerDrawn(Exception):
    pass

# Ballot exceptions
class BallotNotFound(Exception):
    pass

# User exceptions
class UserAlreadyExists(Exception):
    pass

class UserNotFound(Exception):
    pass

class UserInvalidCredentials(Exception):
    pass