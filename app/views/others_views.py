from flask import Blueprint, render_template, request, g

from ..models import Todo, User

bp = Blueprint('others', __name__, url_prefix='/others/')


# 다른 사람의 할 일 검색창을 구성하는 함수
# GET 방식으로 호출 시 menu, keyword, page라는 3개의 인자를 받음
# menu : 검색 기준으로 'title' 또는 'user'의 값을 가짐
# keyword : 검색 시 사용할 키워드, 검색 기준 + 키워드에 맞는 검색 결과가 출력됨
# page : 출력되는 검색 결과의 몇 번째 페이지인지를 나타냄
@bp.route('/')
def search():
    _menu = request.args.get('menu', type=str, default='title')
    _keyword = request.args.get('keyword', type=str, default='')
    _page = request.args.get('page', type=int, default=1)
    others_todo_list = Todo.query.filter(False)
    if _keyword:
        _search = "%%{}%%".format(_keyword)
        if _menu == 'title':
            others_todo_list = Todo.query.filter(
                (Todo.userId != g.user.id) & Todo.name.ilike(_search)
            ).order_by(Todo.time.desc())
        elif _menu == 'user':
            others_todo_list = Todo.query.join(User).filter(
                (Todo.userId != g.user.id) & User.name.ilike(_search)
            )
    others_todo_list = others_todo_list.paginate(page=_page, per_page=10)
    return render_template('others/search.html', others_todo_list=others_todo_list,
                           keyword=_keyword, menu=_menu, page=_page)
