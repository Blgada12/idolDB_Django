from .models import Idol


def get_idol_byId(p0):
    o = Idol.objects
    return o.get(id=p0) if o.filter(id=p0) else False
