class Base(object):

    def load(self):
        print('do logic A')
        print('do logic B')


class Child(Base):

    def load(self):
        super().load()
        print('do logic C')


c = Child()
c.load()   
