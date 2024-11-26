from flask import Blueprint, render_template, request, session, g

from .auth_views import login_required
from ..models import Todo
from datetime import datetime

bp = Blueprint('main', __name__, url_prefix='/')


# 마이페이지를 구성하는 함수
# GET 방식으로 호출 시 page_doing, page_done, keyword라는 3개의 인자를 받음
# page_doing과 page_done은 각각 진행 중인 할 일 목록의 페이지 번호와
# 완료된 할 일 목록의 페이지 번호를 나타냄
# keyword는 검색어가 없을 시에는 ''이 들어가고 검색어가 있을 시에는 검색 키워드가 들어감
@bp.route('/')
@login_required
def mypage():
    page_doing = request.args.get('page_doing', type=int, default=1)
    page_done = request.args.get('page_done', type=int, default=1)
    _keyword = request.args.get('keyword', type=str, default='')
    todo_list = Todo.query.filter((Todo.time > datetime.now()) &
                                  (Todo.userId == g.user.id)).order_by(Todo.priority.desc(), Todo.time.asc())
    done_list = Todo.query.filter((Todo.time <= datetime.now()) &
                                  (Todo.userId == g.user.id)).order_by(Todo.priority.desc(), Todo.time.desc())
    if _keyword:
        _search = "%%{}%%".format(_keyword)
        todo_list = Todo.query.filter((Todo.time > datetime.now()) &
                                      (Todo.userId == g.user.id) &
                                      Todo.name.ilike(_search)).order_by(Todo.priority.desc(), Todo.time.desc())
        done_list = Todo.query.filter((Todo.time <= datetime.now()) &
                                      (Todo.userId == g.user.id) &
                                      Todo.name.ilike(_search)).order_by(Todo.priority.desc(), Todo.time.desc())
    todo_list = todo_list.paginate(page=page_doing, per_page=10)
    done_list = done_list.paginate(page=page_done, per_page=10)
    return render_template('mypage/mypage.html',
                           todo_list=todo_list, page_doing=page_doing,
                           done_list=done_list, page_done=page_done, keyword=_keyword)
