# Maybe class definition
class Maybe(object):
    def __init__(self, data=None, state=0):
        self.data = data
        self.state = state

    def __repr__(self):
        return 'state: {0}, data: {1}'.format(self.state, self.data)

    def __str__(self):
        return self.__repr__()
