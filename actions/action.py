"""Actions break up the process of making a drink into smaller pieces.

They are callables with an optional inspect method."""

class Action(object):
    """Actions processed by the Controller to make drinks."""
    def __call__(self, robot):
        raise NotImplementedError()
    def inspect(self):
        """Returns a description of this action."""
        return (self.__class__.__name__, self.__dict__)
