from TwitterSearch import TwitterSearchOrder


class ExtendedTwitterSearchOrder(TwitterSearchOrder):
    def __init__(self):
        super().__init__()

    def set_since_id(self, since_id):
        """ Sets 'since_id' parameter used to return \
        only tweets generated after the given id

        :param since_id: A tweet id
        :raises: Exception
        """

        if isinstance(since_id, int):
            self.arguments.update({'since_id': '%s' % since_id})
        else:
            raise Exception('Parameter since_id must be an integer')
