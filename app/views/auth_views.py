from flask import Blueprint, url_for, render_template, flash, request, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
import functools

from .. import db
from ..models import User
from ..forms import UserCreateForm, LoginForm, UserModifyForm

bp = Blueprint('auth', __name__, url_prefix='/auth/')


# 회원 가입과 관련된 함수
# GET 방식으로 호출 시 회원 가입 창을 띄움
# POST 방식으로 호출 시 유효한 데이터면 이를 회원 정보에 저장, 아니면 오류 메시지
@bp.route('/signup/', methods=('GET', 'POST'))
def signup():
    form = UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(id=form.id.data).first()
        if not user:
            user = User(id=form.id.data,
                        name=form.name.data,
                        password=generate_password_hash(form.password1.data)
                        )
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.mypage'))
        else:
            flash('이미 존재하는 아이디입니다.')
    return render_template('auth/signup.html', form=form)


# 로그인과 관련된 함수
# GET 방식으로 호출 시 로그인 창을 띄움
# POST 방식으로 호출되고 아이디와 비밀번호 쌍이 유효하면 로그인을 수행, 아닐 시 오류 메시지 출력
@bp.route('/login/', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user = User.query.filter_by(id=form.id.data).first()
        if not user:
            error = "존재하지 않는 사용자입니다."
        elif not check_password_hash(user.password, form.password.data):
            error = "비밀번호가 올바르지 않습니다."
        if error is None:
            session.clear()
            session['userId'] = user.id
            _next = request.args.get('next', '')
            if _next:
                return redirect(_next)
            else:
                return redirect(url_for('main.mypage'))
        flash(error)
    return render_template('auth/login.html', form=form)


# 로그아웃과 관련된 함수
# 호출되면 로그아웃을 수행함
@bp.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


# 로그인 되어 있을 때 세션에서 유저 정보를 불러오는 함수
# 점프 투 플라스크 3-07장 로그인과 로그아웃 부분 참고하여 만들었음
@bp.before_app_request
def load_logged_in_user():
    userId = session.get('userId')
    if userId is None:
        g.user = None
    else:
        g.user = User.query.get(userId)


# 로그인 되어 있을 때만 페이지에 들어갈 수 있게 해주는 모디파이어
# 점프 투 플라스크 3-08장 모델 수정하기 부분 참고하여 만들었음
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            _next = request.url if request.method == 'GET' else ''
            return redirect(url_for('auth.login', next=_next))
        return view(*args, **kwargs)
    return wrapped_view


# 유저 정보 수정과 관련된 함수
# GET 방식 호출 시 유저 정보 변경 화면을 띄움
# POST 방식 호출 시 폼에 입력된 내용에 따라 유저 정보 변경
@bp.route('/modify-user/', methods=('GET', 'POST'))
@login_required
def modify_user():
    user = g.user
    if request.method == "POST":
        form = UserModifyForm()
        if form.validate_on_submit():
            form.populate_obj(user)
            db.session.commit()
            return redirect(url_for('main.mypage'))
    else:
        form = UserModifyForm(obj=user)
    return render_template('mypage/user_info_modify.html', form=form)


