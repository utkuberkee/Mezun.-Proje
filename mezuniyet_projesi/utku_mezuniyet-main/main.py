# İçe aktar
from flask import Flask, render_template,request, redirect
# Veri tabanı kitaplığını bağlama
from flask_sqlalchemy import SQLAlchemy
import os
from model import get_class

app = Flask(__name__)
# SQLite'ı bağlama
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Veri tabanı oluşturma
db = SQLAlchemy(app)
# Tablo oluşturma

class Card(db.Model):
    # Sütun oluşturma
    # id
    id = db.Column(db.Integer, primary_key=True)
    # Başlık
    title = db.Column(db.String(100), nullable=False)
    # Tanım
    subtitle = db.Column(db.String(300), nullable=False)
    # Metin
    text = db.Column(db.Text, nullable=False)

    # Nesnenin ve kimliğin çıktısı
    def __repr__(self):
        return f'<Card {self.id}>'
    

# Görev #1. Kullanıcı tablosu oluşturun
class User(db.Model):
	# Sütunlar oluşturuluyor
	#id
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	# Giriş
	login = db.Column(db.String(100), nullable=False)
	# Şifre
	password = db.Column(db.String(30), nullable=False)


# Yüklenen dosyaların kaydedileceği dizin
UPLOAD_FOLDER = 'images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# İzin verilen dosya uzantıları
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Dosyanın izin verilen bir uzantıya sahip olup olmadığını kontrol eden fonksiyon
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/goruntu')
def goruntu():
    return render_template('goruntu.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # Görseli model ile analiz et
        class_name, confidence = get_class(file_path)
        
        # Sonuçları kullanıcıya göster
        return render_template('result.html', class_name=class_name, confidence=confidence, filename=filename)

    return 'Geçersiz dosya tipi'

# İçerik sayfasını çalıştırma
@app.route('/', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        form_login = request.form['email']
        form_password = request.form['password']
        
        # Kullanıcı doğrulama
        users_db = User.query.all()  # Veritabanındaki tüm kullanıcıları al
        for user in users_db:
            #Görev #4. Kullanıcıyı yetkilendir
            if form_login == user.login and form_password == user.password:
                return redirect('/index')  # Giriş başarılıysa yönlendirme yap
            else:
                error = 'Incorrect login or password'
                return render_template('login.html', error=error)

   
    return render_template('login.html')



@app.route('/reg', methods=['GET','POST'])
def reg():
    if request.method == 'POST':
        login= request.form['email']
        password = request.form['password']
        
        #Ödev #3 Kullanıcı verilerinin veri tabanına kaydedilmesini sağlayın
        user= User(login=login, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    
    else:    
        return render_template('registration.html')


# İçerik sayfasını çalıştırma
@app.route('/index')
def index():
    # Veri tabanı girişlerini görüntüleme
    cards = Card.query.order_by(Card.id).all()
    return render_template('index.html', cards=cards)

# Kayıt sayfasını çalıştırma
@app.route('/card/<int:id>')
def card(id):
    card = Card.query.get(id)

    return render_template('card.html', card=card)

# Giriş oluşturma sayfasını çalıştırma
@app.route('/create')
def create():
    return render_template('create_card.html')

# Giriş formu
@app.route('/form_create', methods=['GET','POST'])
def form_create():
    if request.method == 'POST':
        title =  request.form['title']
        subtitle =  request.form['subtitle']
        text =  request.form['text']

        # Veri tabanına gönderilecek bir nesne oluşturma
        card = Card(title=title, subtitle=subtitle, text=text)

        db.session.add(card)
        db.session.commit()
        return redirect('/index')
    else:
        return render_template('create_card.html')





if __name__ == "__main__":
    app.run(debug=True)
