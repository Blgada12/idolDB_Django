class OnceAtSameDay(Exception):
    def __init__(self):
        self.msg = '방명록은 하루에 한번만 쓸 수 있습니다.'

    def __str__(self):
        return self.msg


