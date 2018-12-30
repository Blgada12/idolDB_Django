from django.shortcuts import redirect

from idolmaster.models import Production
from users.models import User


def productions_click_controller(req):
    productions: str = req.GET.get('productions')
    if productions:
        req.session['productions'] = productions.split(',')

        return True

    clicked: str = req.GET.get('clicked')
    if clicked:
        pro_selected: list = req.session.get('productions')
        pro_selected.append(clicked)
        pro_selected.sort()
        req.session['productions'] = pro_selected

        return True

    unclicked: str = req.GET.get('unclicked')
    if unclicked:
        pro_selected: list = req.session.get('productions')
        pro_selected.remove(unclicked)
        req.session['productions'] = pro_selected

        return True
    return False

def auto_login_controller(req):
    user = None
    isLogin = req.session.get('isLogin', False)
    if isLogin:
        ou = User.objects
        try:
            user = ou.get(token=req.session.get('token'))
        except User.DoesNotExist:
            req.session['isLogin'] = False
            return redirect('idolMain')
    return isLogin, user


def productions_filter_controller(req):
    op = Production.objects
    selected_pro = list()
    if req.session.get('productions', False):
        for i in req.session.get('productions'):
            selected_pro.append(op.get(id=int(i)))
    else:
        tmp = list()
        for i in op.all():
            tmp.append(str(i.id))
            selected_pro.append(i)
        req.session['productions'] = tmp
    return op, selected_pro
