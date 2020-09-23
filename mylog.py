class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# TODO: to be implemented
class Logger():
    debug_mode = True

    def warn(self, msg):
        if self.debug_mode:
            print(bcolors.WARNING + msg + bcolors.ENDC)

    def ok(self, msg):
        if self.debug_mode:
            print(bcolors.OKGREEN + msg + bcolors.ENDC)

    def info(self, msg):
        if self.debug_mode:
            print(bcolors.OKBLUE + msg + bcolors.ENDC)

    def bold(self, msg):
        if self.debug_mode:
            print(bcolors.BOLD + msg + bcolors.ENDC)

    def underline(self, msg):
        if self.debug_mode:
            print(bcolors.UNDERLINE + msg + bcolors.ENDC)


logger = Logger()


class Animal:
    SIZES = lambda: ["Huge", "Big", "Medium", "Small"]


class Horse(Animal):
    def printSize(self):
        print(Animal.SIZES()[1])

h= Horse()
h.printSize()
h.__class__.SIZES()
