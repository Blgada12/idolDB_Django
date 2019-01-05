import math
from datetime import datetime, timedelta, time

from django.shortcuts import render, redirect

# Create your views here.
from django.views import View

from community.exceptions import OnceAtSameDay
from community.forms import CameLogForm
from community.models import CameLog
from community.utils import auto_login_controller
from users.models import User

AFTER_INDEX = 3
PAGE_INDEX = 2


class CameLogView(View):
    def get(self, req):

        if req.GET.get('index'):
            index = int(req.GET.get('index'))-1
            if index == 0:
                return redirect('cameLog')
        else:
            index = 0

        isLogin, user = auto_login_controller(req)
        rDict = dict(isLogin=isLogin, user=user)

        result = CameLog.objects.order_by('-date')

        if index > 0:
            rDict['canDown'] = index
        else:
            rDict['canDown'] = None
        if index + 2 < int(math.ceil(len(result) / PAGE_INDEX)) + 1:
            rDict['canUp'] = index + 2
        else:
            rDict['canUp'] = None
        rindex = list(
            set(range(index - 1, index + 4)) & set(range(1, int(math.ceil(len(result) / PAGE_INDEX)) + 1)))
        rindex.sort()
        rDict['full_index'] = rindex

        rDict['isLogin'] = isLogin
        rDict['now'] = 'camelog'
        rDict['now_index'] = index + 1
        rDict['camelogs'] = result[PAGE_INDEX * index:PAGE_INDEX * (index + 1)]
        return render(req, 'community/camelog.html', rDict)

    def post(self, req):
        isLogin, user = auto_login_controller(req)
        rDict = dict(isLogin=isLogin, user=user)
        ou = User.objects
        oc = CameLog.objects

        try:
            camelog = CameLogForm(req.POST).get_commit_data()
            today = datetime.now().date()
            tomorrow = today + timedelta(1)
            today_start = datetime.combine(today, time())
            today_end = datetime.combine(tomorrow, time())

            account = ou.get(token=req.session['token'])
            if oc.filter(user=account).order_by('-date').filter(date__gte=today_start).filter(
                    date__lt=today_end).exists():
                raise OnceAtSameDay
            camelog.user = user
            camelog.save()
            rDict['error'] = '작성되었습니다.'
        except ValueError:
            rDict['error'] = '올바른 데이터를 넣어주세요.'
        except OnceAtSameDay as e:
            rDict['error'] = e.msg
        finally:
            if req.GET.get('index'):
                index = int(req.GET.get('index')) - 1
            else:
                index = 0

            result = CameLog.objects.order_by('-date')

            if not index in range(1, int(math.ceil(len(result) / PAGE_INDEX)) + 1):
                req.session['index_search'] = 1
                index = 0

            if index > 0:
                rDict['canDown'] = index
            else:
                rDict['canDown'] = None
            if index + 2 < int(math.ceil(len(result) / PAGE_INDEX)) + 1:
                rDict['canUp'] = index + 2
            else:
                rDict['canUp'] = None
            rindex = list(
                set(range(index - 1, index + 4)) & set(range(1, int(math.ceil(len(result) / PAGE_INDEX)) + 1)))
            rindex.sort()
            rDict['full_index'] = rindex

            rDict['isLogin'] = req.session['isLogin']
            rDict['now'] = 'camelog'
            rDict['camelogs'] = result[PAGE_INDEX * index:PAGE_INDEX * (index + 1)]
            return render(req, 'community/camelog.html', rDict)



