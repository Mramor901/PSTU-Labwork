from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Замените на собственный секретный ключ
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель пользователя для регистрации и авторизации
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Модель дисциплины (курса)
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

# Автоматическое создание таблиц и добавление тестовых данных по дисциплинам
@app.before_request
def create_tables():
    db.create_all()
    if Course.query.count() == 0:
        courses = [
            Course(title='Математика', description='Курс по математике, охватывающий алгебру, геометрию и математический анализ.'),
            Course(title='Физика', description='Курс по физике с акцентом на законы механики и электромагнетизма.'),
            Course(title='История', description='Курс по истории, включающий изучение мировых цивилизаций.')
        ]
        db.session.add_all(courses)
        db.session.commit()

# Главная страница с перечнем учебных дисциплин
@app.route('/')
def index():
    courses = Course.query.all()
    return render_template('index.html', courses=courses)

# Страница отдельной дисциплины. Если дисциплины нет — выведется 404
@app.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course.html', course=course)

# Регистрация пользователя
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Имя пользователя уже существует!')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация успешна! Теперь вы можете войти.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Авторизация пользователя
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash('Неверное имя пользователя или пароль!')
            return redirect(url_for('login'))
        session['user_id'] = user.id
        flash('Вы успешно вошли!')
        return redirect(url_for('index'))
    return render_template('login.html')

# Выход из системы
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Вы вышли из системы.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
