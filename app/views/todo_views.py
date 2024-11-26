from flask import Blueprint, redirect, url_for, render_template, flash, request, session, g
from datetime import *

from .. import db
from .auth_views import login_required
from ..forms import TodoForm, DetailForm, CommentForm
from ..models import Todo, Detail, Comment

bp = Blueprint('todo', __name__, url_prefix='/todo/')


# 새로운 할 일을 만드는 창에 관련된 함수
# GET 방식으로 호출시 새로운 할 일을 만드는 페이지를 출력함
# POST 방식으로 호출 및 해당 창에 입력한 데이터가 유효한 경우
# 입력된 데이터를 바탕으로 새로운 할 일을 생성함
# 입력된 데이터가 유효하지 않은 경우 오류 메시지를 띄움
@bp.route('/create/', methods=('GET', 'POST'))
@login_required
def create():
    form = TodoForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = request.form['name']
        _date = request.form['date']
        _time = request.form['time']
        date_and_time = _date + ' ' + _time
        date_and_time = datetime.strptime(date_and_time, "%Y-%m-%d %H:%M")
        info = request.form['info']

        todo = Todo(name=name, userId=g.user.id, time=date_and_time, info=info)
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('main.mypage'))

    return render_template('todo/todo_create.html', form=form)


# 기존에 만든 할 일을 수정하는 페이지에 관련된 함수
# GET 방식으로 호출 시 todo_id에 해당하는 할 일의 정보를 담은 할 일 정보 수정 창을 띄움
# POST 방식으로 호출 시 입력한 수정된 할 일 정보가 유효한 경우 변경된 정보를 todo_id에 해당하는 할 일 위치에 저장함
# 입력된 정보가 유효하지 않은 경우 오류 메시지를 띄움
@bp.route('/modify/<int:todo_id>', methods=('GET', 'POST'))
@login_required
def modify(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if g.user != todo.user:
        return redirect(url_for('todo.detail', todo_id=todo.id))
    if request.method == 'POST':
        form = TodoForm()
        if form.validate_on_submit():
            date_and_time = request.form['date'] + ' ' + request.form['time']
            todo.name = request.form['name']
            todo.time = datetime.strptime(date_and_time, "%Y-%m-%d %H:%M")
            todo.info = request.form['info']
            db.session.commit()
            return redirect(url_for('todo.detail', todo_id=todo.id))
    else:
        form = TodoForm(name=todo.name, date=todo.time.date(),
                        time=todo.time.time(), info=todo.info)
    return render_template('todo/todo_modify.html', form=form, todo=todo)


# 기존에 만들어진 할 일을 삭제하는 페이지에 관련된 함수
# 호출 시 삭제하려는 유저가 페이지의 작성자인 경우에는 DB에서 해당 할 일을 삭제한 후 마이페이지로 이동한다.
@bp.route('/delete/<int:todo_id>')
@login_required
def delete(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if g.user != todo.user:
        return redirect(url_for('todo.detail', todo_id=todo.id))
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('main.mypage'))


# 할 일의 중요도를 체크/해제하는 함수
# id가 todo_id인 할 일을 작성한 유저가 해당 함수를 호출하는 유저인 경우에만 작동 수행
# priority가 기존에 1인 경우 0으로, 0인 경우 1로 바꾼다.
@bp.route('/priority/<int:todo_id>')
@login_required
def priority(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if g.user.id != todo.userId:
        return redirect(url_for('todo.detail', todo_id=todo.id))
    todo.priority = 1 - todo.priority
    db.session.commit()
    return redirect(url_for('todo.detail', todo_id=todo.id))


# 할 일의 좋아요를 체크/해제하는 함수
# 기존에 id가 todo_id인 할 일을 작성한 유저가 아닌 유저가 해당 함수를 호출하는 경우에만 작동 수행
# 함수 호출 유저가 기존에 좋아요를 누른 경우 해당 좋아요를 취소함
# 함수 호출 유저가 기존에 좋아요를 누르지 않은 경우에 해당 유저가 해당 할 일에 좋아요를 눌렀음을 DB에 저장함
@bp.route('/like/<int:todo_id>')
@login_required
def like(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if g.user.id == todo.userId:
        flash("자기 것에는 좋아요를 누를 수 없다.")
    else:
        if g.user not in todo.like:
            todo.like.append(g.user)
            db.session.commit()
        else:
            todo.like.remove(g.user)
            db.session.commit()
    return redirect(url_for('todo.detail', todo_id=todo.id))


# 할 일에 댓글을 저장하는 함수
# GET 방식으로 해당 함수를 호출했을 때에는 해당 할 일의 정보, 세부 할 일, 댓글들을 화면에 띄우는 역할을 함
# POST 방식으로 해당 함수를 호출했을 때에는 해당 화면의 댓글 작성 폼에 작성된 댓글을 DB에 저장함
@bp.route('/detail/<int:todo_id>', methods=('GET', 'POST'))
@login_required
def detail(todo_id):
    form = CommentForm()
    if request.method == 'POST' and form.validate_on_submit():
        _comment = Comment(todoId=todo_id, userId=g.user.id,
                           text=request.form['text'],
                           writeTime=datetime.now())
        db.session.add(_comment)
        db.session.commit()
        return redirect(url_for('todo.detail', todo_id=todo_id))
    todo = Todo.query.get_or_404(todo_id)
    detail_list = todo.detail_set
    comment_list = todo.todo_comment_set
    return render_template('detail/detail.html', form=form, todo=todo,
                           detail_list=detail_list, comment_list=comment_list)


# 할 일의 세부 할 일을 새로 만드는 화면에 관련된 함수
# GET 방식으로 호출 시 id가 todo_id인 할 일의 세부 할 일을 만드는 화면을 출력한다.
# POST 방식으로 해당 함수를 호출했을 때에는 해당 화면의 입력 폼에 입력된 정보를 바탕으로 id가 todo_id인 할 일에 세부 할 일을 추가함
@bp.route('/detail/create/<int:todo_id>', methods=('GET', 'POST'))
@login_required
def detail_create(todo_id):
    form = DetailForm()
    if request.method == 'POST' and form.validate_on_submit():
        _detail = Detail(todoId=todo_id,
                         name=request.form['name'],
                         progress=request.form['progress'])
        db.session.add(_detail)
        db.session.commit()
        return redirect(url_for('todo.detail', todo_id=todo_id))
    return render_template('detail/detail_create.html', form=form, todo_id=todo_id)


# 할 일의 세부 할 일을 수정하는 화면에 관련된 함수
# GET 방식으로 호출했을 때는 id가 detail_id인 세부 할 일을 수정하는 화면 출력
# POST 방식으로 호출했을 때는 id가 detail_id인 세부 할 일 내용을 사용자가 새로 입력한 내용으로 바꿈
@bp.route('/detail/modify/<int:detail_id>', methods=('GET', 'POST'))
@login_required
def detail_modify(detail_id):
    _detail = Detail.query.get_or_404(detail_id)
    todo_id = _detail.todoId
    todo = Todo.query.get_or_404(todo_id)
    if g.user != todo.user:
        return redirect(url_for('todo.detail', todo_id=todo.id))
    if request.method == 'POST':
        form = DetailForm()
        if form.validate_on_submit():
            form.populate_obj(obj=_detail)
            db.session.commit()
            return redirect(url_for('todo.detail', todo_id=todo_id))
    else:
        form = DetailForm(obj=_detail)
    return render_template('detail/detail_modify.html', form=form, todo_id=todo_id)


# 할 일의 세부 할 일을 삭제하는 것과 관련된 함수
# 호출 시 호출한 유저가 id가 detail_id인 세부 할 일의 작성자라면 해당 세부 할 일을 삭제
# 해당 세부 할 일을 갖고 있는 할 일의 화면으로 이동
@bp.route('/detail/delete/<int:detail_id>')
@login_required
def detail_delete(detail_id):
    _detail = Detail.query.get_or_404(detail_id)
    _todo = _detail.todo
    if g.user != _todo.user:
        return redirect(url_for('todo.detail', todo_id=_todo.id))
    db.session.delete(_detail)
    db.session.commit()
    return redirect(url_for('todo.detail', todo_id=_todo.id))


# 할 일에 달린 댓글을 삭제하는 함수
# id가 comment_id인 댓글 삭제
# 댓글 작성자만 실행 가능
@bp.route('/comment/delete/<int:comment_id>')
@login_required
def comment_delete(comment_id):
    _comment = Comment.query.get_or_404(comment_id)
    if g.user != _comment.user:
        return redirect(url_for('todo.detail', todo_id=_comment.todoId))
    db.session.delete(_comment)
    db.session.commit()
    return redirect(url_for('todo.detail', todo_id=_comment.todoId))
