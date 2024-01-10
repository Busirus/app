from flask import render_template, request, redirect, url_for, flash
from flask import session 
from app import app, db
from app.models import Post, User, Reply 
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os
import random

def generate_captcha_question():
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    question = f"Quelle est la somme de {num1} et {num2}?"
    answer = num1 + num2
    return question, answer

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
@app.route('/index')
@app.route('/index/<int:page>')
def index(page=1):
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, 10, False)
    return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    question, answer = generate_captcha_question()
    session['captcha_answer'] = answer

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        captcha_response = request.form['captcha']
        
        if session.get('captcha_answer') != int(captcha_response):
            flash('Réponse CAPTCHA incorrecte.')
            return render_template('register.html', captcha_question=question)

        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return render_template('register.html', captcha_question=question)

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html', captcha_question=question)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('admin'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    question, answer = generate_captcha_question()
    session['captcha_answer'] = answer

    if request.method == 'POST':
        content = request.form['content']
        file = request.files['file']
        captcha_response = request.form['captcha']

        if session.get('captcha_answer') != int(captcha_response):
            flash('Réponse CAPTCHA incorrecte.')
            return render_template('post.html', captcha_question=question)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            ip_address = request.remote_addr
            new_post = Post(content=content, image_path=file_path, ip_address=ip_address, user_id=current_user.id)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            flash('Invalid file type. Only image files are allowed.')

    return render_template('post.html', captcha_question=question)

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user and not current_user.is_admin:
        return redirect(url_for('index'))
    if request.method == 'POST':
        post.content = request.form['content']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_post.html', post=post)

@app.route('/reply/<int:post_id>', methods=['GET', 'POST'])
@login_required
def reply(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        content = request.form['content']
        reply = Reply(content=content, user_id=current_user.id, post_id=post_id)
        db.session.add(reply)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('reply.html', post=post)


@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user and not current_user.is_admin:
        return redirect(url_for('index'))
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))
