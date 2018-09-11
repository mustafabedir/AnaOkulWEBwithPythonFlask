from flask import Flask, render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,TextField,StringField,TextAreaField,PasswordField, validators, SelectField, DateField
from passlib.hash import sha256_crypt
from functools import wraps
from IPython.display import display, HTML
import sys

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "loggedIn" in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for("login"))
    return decorated_function

class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Şifre")

class RegisterForm(Form):
    username = StringField("Kullanıcı Adı", validators=[
        validators.length(min=4,max=35, message="En Az 4 En Fazla 35 Karakter Olabilir!"),
        validators.DataRequired(message="Kullanıcı Adını Giriniz!")
    ])
    password = PasswordField("Şifre", validators=[
        validators.DataRequired(message="Parola Belirleyin!"),
        validators.EqualTo(fieldname = "confirm", message= "Parolanız Uyuşmuyor")
    ])
    confirm = PasswordField("Doğrula")

class KullaniciForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Şifre")

class VeliForm(Form):
    veliadsoyad = StringField("Veli Ad-Soyad")
    velitelefon = StringField("Veli Telefon")
    velitckn = StringField("Veli TCKN")
    velimail = StringField("Veli E-Mail")

class SinifForm(Form):
    sinifad = StringField("Sınıf Adı")
    mevcut = StringField("Mevcut")

class OgretmenForm(Form):
    ogretmenadsoyad = StringField("Öğretmen Ad-Soyad")
    ogretmentel = StringField("Öğretmen Tel")
    sinif = SelectField('Sınıf', coerce=int, choices=[])

class OgrenciForm(Form):
    ogrenciadsoyad = StringField("Öğrenci Ad-Soyad")
    ogrenciyas = StringField("Öğrenci Yaş")
    ogrencitckn = StringField("Öğrenci TCKN")
    veli = SelectField('Veli', coerce=int, choices=[])
    sinif = SelectField('Sınıf:', coerce=int, choices=[])

app = Flask(__name__)
app.secret_key="anaokul"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "anaokuldb"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


@app.route("/index")
def index():
    return render_template("index.html")

#Kullanıcı İşlemleri

@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        username = form.username.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        sorgu = "select * from kullanici where kullaniciad = %s and kullanicisifre = %s"
        result = cursor.execute(sorgu,(username, password))

        if result > 0:
            session["loggedIn"]= True
            session["username"]=username
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))
            mysql.connection.commit()
            cursor.close()
    else:
        return render_template("login.html", form = form)
        mysql.connection.commit()
        cursor.close()

@app.route("/register", methods=["GET","POST"])
@login_required
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        username = form.username.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        sorgu = "Insert Into kullanici(kullaniciad, kullanicisifre) values(%s,%s)"
        cursor.execute(sorgu,(username,password))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("index"))
    else:
        return render_template("register.html", form = form)

@app.route("/kullanici", methods=["GET","POST"])
@login_required
def kullanici():
    cursor = mysql.connection.cursor()
    sorgu = "select * from kullanici"
    result = cursor.execute(sorgu,)

    if result >0:
        kullanicilar = cursor.fetchall()
        return render_template("kullanici.html", kullanicilar = kullanicilar)
    else:
        return render_template("kullanici.html")

@app.route("/editkullanici/<string:id>", methods=["GET","POST"])
@login_required
def editkullanici(id):
    if request.method=="GET":
        cursor = mysql.connection.cursor()
        sorgu = "select * from kullanici where kullaniciid = %s"
        result = cursor.execute(sorgu,(id,))

        if result >0:
            kullanici = cursor.fetchone()
            form = KullaniciForm()
            form.username.data = kullanici["kullaniciad"]
            form.password.data = kullanici["kullanicisifre"]
            return render_template("editkullanici.html", form = form)
        else:
            return render_template("index.html")
    else:
        form = KullaniciForm(request.form)
        newKullaniciAd = form.username.data
        newKullaniciSifre = form.password.data

        sorgu2 = "update kullanici set kullaniciad = %s , kullanicisifre = %s where kullaniciid = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(sorgu2,(newKullaniciAd,newKullaniciSifre,id))
        mysql.connection.commit()
        return redirect(url_for("kullanici"))

@app.route("/deletekullanici/<string:id>")
@login_required
def deletekullanici(id):
    cursor = mysql.connection.cursor()
    sorgu = "select * from kullanici where kullaniciid = %s"
    result = cursor.execute(sorgu,(id,))

    if result >0:
        sorgu2 = "delete from kullanici where kullaniciid = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("kullanici"))
    else:
        return redirect(url_for("kullanici"))


#Veli İşlemleri
@app.route("/veli", methods =["GET","POST"])
@login_required
def veli():
    cursor = mysql.connection.cursor()
    sorgu = "select * from veli"
    result = cursor.execute(sorgu,)

    if result >0:
        veliler = cursor.fetchall()
        return render_template("veli.html", veliler = veliler)
    else:
        return render_template("veli.html")

@app.route("/addveli", methods=["GET","POST"])
@login_required
def addveli():
    form = VeliForm(request.form)
    if request.method == "POST" and form.validate():
        veliadsoyad = form.veliadsoyad.data
        velitelefon = form.velitelefon.data
        velitckn = form.velitckn.data
        velimail = form.velimail.data

        cursor = mysql.connection.cursor()
        sorgu = "Insert Into veli(veliadsoyad, velitelefon, velitckn, velimail) values(%s,%s,%s,%s)"
        cursor.execute(sorgu,(veliadsoyad,velitelefon,velitckn,velimail))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("veli"))
    else:
        return render_template("/addveli.html", form = form)

@app.route("/editveli/<string:id>",methods=["GET","POST"])
@login_required
def editveli(id):
    if request.method=="GET":
        cursor = mysql.connection.cursor()
        sorgu = "select * from veli where veliid = %s"
        result = cursor.execute(sorgu,(id,))

        if result >0:
            veli = cursor.fetchone()
            form = VeliForm()
            form.veliadsoyad.data = veli["veliadsoyad"]
            form.velitelefon.data = veli["velitelefon"]
            form.velitckn.data = veli["velitckn"]
            form.velimail.data = veli["velimail"]
            return render_template("editveli.html", form = form)
        else:
            return render_template("index.html")
    else:
        form = VeliForm(request.form)
        newVeliAdSoyad = form.veliadsoyad.data
        newVeliTelefon = form.velitelefon.data
        newVeliTCKN = form.velitckn.data
        newVeliMail = form.velimail.data
        sorgu2 = "update veli set veliadsoyad = %s , velitelefon = %s , velitckn = %s , velimail = %s where veliid = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(sorgu2,(newVeliAdSoyad,newVeliTelefon,newVeliTCKN,newVeliMail,id))
        mysql.connection.commit()
        return redirect(url_for("veli"))

@app.route("/deleteveli/<string:id>")
@login_required
def deleteveli(id):
    cursor = mysql.connection.cursor()
    sorgu = "select * from veli where veliid = %s"
    result = cursor.execute(sorgu,(id,))
    if result >0:
        sorgu2 = "delete from veli where veliid = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("veli"))
    else:
        return redirect(url_for("veli"))

#Sınıf İşlemleri
@app.route("/sinif", methods =["GET","POST"])
@login_required
def sinif():
    cursor = mysql.connection.cursor()
    sorgu = "select * from sinif"
    result = cursor.execute(sorgu,)

    if result >0:
        siniflar = cursor.fetchall()
        return render_template("sinif.html", siniflar = siniflar)
    else:
        return render_template("sinif.html")

@app.route("/addsinif", methods=["GET","POST"])
@login_required
def addsinif():
    form = SinifForm(request.form)
    if request.method == "POST" and form.validate():
        sinifad = form.sinifad.data
        mevcut = form.mevcut.data
        
        cursor = mysql.connection.cursor()
        sorgu = "Insert Into sinif(sinifad, mevcut) values(%s,%s)"
        cursor.execute(sorgu,(sinifad, mevcut))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("sinif"))
    else:
        return render_template("/addsinif.html", form = form)

@app.route("/editsinif/<string:id>",methods=["GET","POST"])
@login_required
def editsinif(id):
    if request.method=="GET":
        cursor = mysql.connection.cursor()
        sorgu = "select * from sinif where sinifid = %s"
        result = cursor.execute(sorgu,(id,))

        if result >0:
            sinif = cursor.fetchone()
            form = SinifForm()
            form.sinifad.data = sinif["sinifad"]
            form.mevcut.data = sinif["mevcut"]
            return render_template("editsinif.html", form = form)
        else:
            return render_template("index.html")
    else:
        form = SinifForm(request.form)
        newSinifAd = form.sinifad.data
        newMevcut = form.mevcut.data
        sorgu2 = "update sinif set sinifad = %s , mevcut = %s where sinifid = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(sorgu2,(newSinifAd,newMevcut,id))
        mysql.connection.commit()
        return redirect(url_for("sinif"))

@app.route("/deletesinif/<string:id>")
@login_required
def deletesinif(id):
    cursor = mysql.connection.cursor()
    sorgu = "select * from sinif where sinifid = %s"
    result = cursor.execute(sorgu,(id,))
    if result >0:
        sorgu2 = "delete from sinif where sinifid = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("sinif"))
    else:
        return redirect(url_for("sinif"))


#Ogretmen İşlemleri
@app.route("/ogretmen", methods =["GET","POST"])
@login_required
def ogretmen():
    cursor = mysql.connection.cursor()
    sorgu = "select * from ogretmen inner join sinif on ogretmen.sinifid = sinif.sinifid"
    result = cursor.execute(sorgu,)

    if result >0:
        ogretmenler = cursor.fetchall()
        return render_template("ogretmen.html", ogretmenler = ogretmenler)
    else:
        return render_template("ogretmen.html")

@app.route("/addogretmen", methods=["GET","POST"])
@login_required
def addogretmen():
    form = OgretmenForm(request.form)
    cursor = mysql.connection.cursor()
    sorgu = "select * from sinif"
    result = cursor.execute(sorgu,)
    form.sinif.choices = [(sinif['sinifid'],sinif['sinifad']) for sinif in cursor.fetchall()]
    if request.method == "POST" and form.validate():
        ogretmenadsoyad = form.ogretmenadsoyad.data
        ogretmentel = form.ogretmentel.data
        sinif = form.sinif.data
        
        cursor = mysql.connection.cursor()
        sorgu = "Insert Into ogretmen(ogretmenadsoyad, ogretmentel, sinifid) values(%s,%s,%s)"
        cursor.execute(sorgu,(ogretmenadsoyad, ogretmentel, sinif))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("ogretmen"))
    else:
        return render_template("/addogretmen.html", form = form)

@app.route("/editogretmen/<string:id>",methods=["GET","POST"])
@login_required
def editogretmen(id):
    if request.method=="GET":
        cursor = mysql.connection.cursor()
        sorgu = "select * from ogretmen where ogretmenid = %s"
        result = cursor.execute(sorgu,(id,))

        if result >0:
            ogretmen = cursor.fetchone()
            form = OgretmenForm()
            form.ogretmenadsoyad.data = ogretmen["ogretmenadsoyad"]
            form.ogretmentel.data = ogretmen["ogretmentel"]
            cursor2 = mysql.connection.cursor()
            sorgu2 = "select * from sinif"
            cursor2.execute(sorgu2,)
            form.sinif.choices = [(sinif['sinifid'],sinif['sinifad']) for sinif in cursor2.fetchall()]
            return render_template("editogretmen.html", form = form)
        else:
            return render_template("index.html")
    else:
        form = OgretmenForm(request.form)
        newogretmenadsoyad = form.ogretmenadsoyad.data
        newogretmentel = form.ogretmentel.data
        newsinif = form.sinif.data
        sorgu2 = "update ogretmen set ogretmenadsoyad = %s , ogretmentel = %s , sinifid = %s where ogretmenid = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(sorgu2,(newogretmenadsoyad,newogretmentel,newsinif,id))
        mysql.connection.commit()
        return redirect(url_for("ogretmen"))

@app.route("/deleteogretmen/<string:id>")
@login_required
def deleteogretmen(id):
    cursor = mysql.connection.cursor()
    sorgu = "select * from ogretmen where ogretmenid = %s"
    result = cursor.execute(sorgu,(id,))
    if result >0:
        sorgu2 = "delete from ogretmen where ogretmenid = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("ogretmen"))
    else:
        return redirect(url_for("ogretmen"))

#Ogrenci İşlemleri
@app.route("/ogrenci", methods =["GET","POST"])
@login_required
def ogrenci():
    cursor = mysql.connection.cursor()
    sorgu = "select * from ogrenci inner join sinif on ogrenci.sinifid = sinif.sinifid inner join veli on ogrenci.veliid = veli.veliid"
    result = cursor.execute(sorgu,)

    if result >0:
        ogrenciler = cursor.fetchall()
        return render_template("ogrenci.html", ogrenciler = ogrenciler)
    else:
        return render_template("ogrenci.html")

@app.route("/addogrenci", methods=["GET","POST"])
@login_required
def addogrenci():
    form = OgrenciForm(request.form)
    cursor = mysql.connection.cursor()
    sorgu = "select * from sinif"
    result = cursor.execute(sorgu,)
    form.sinif.choices = [(sinif['sinifid'],sinif['sinifad']) for sinif in cursor.fetchall()]
    sorgu2 = "select * from veli"
    result2 = cursor.execute(sorgu2,)
    form.veli.choices = [(veli['veliid'],veli['veliadsoyad']) for veli in cursor.fetchall()]
    
    if request.method == "POST" and form.validate():
        ogrenciadsoyad = form.ogrenciadsoyad.data
        ogrenciyas = form.ogrenciyas.data
        ogrencitckn = form.ogrencitckn.data
        veli = form.veli.data
        sinif = form.sinif.data
        
        cursor = mysql.connection.cursor()
        sorgu = "Insert Into ogrenci(ogrenciadsoyad, ogrenciyas,ogrencitckn,veliid, sinifid) values(%s,%s,%s,%s,%s)"
        cursor.execute(sorgu,(ogrenciadsoyad,ogrenciyas, ogrencitckn,veli, sinif))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("ogrenci"))
    else:
        return render_template("/addogrenci.html", form = form)

@app.route("/editogrenci/<string:id>",methods=["GET","POST"])
@login_required
def editogrenci(id):
    if request.method=="GET":
        cursor = mysql.connection.cursor()
        sorgu = "select * from ogrenci where ogrenciid = %s"
        result = cursor.execute(sorgu,(id,))

        if result >0:
            ogrenci = cursor.fetchone()
            form = OgrenciForm()
            form.ogrenciadsoyad.data = ogrenci["ogrenciadsoyad"]
            form.ogrenciyas.data = ogrenci["ogrenciyas"]
            form.ogrencitckn.data = ogrenci["ogrencitckn"]
            cursor2 = mysql.connection.cursor()
            sorgu2 = "select * from sinif"
            cursor2.execute(sorgu2,)
            form.sinif.choices = [(sinif['sinifid'],sinif['sinifad']) for sinif in cursor2.fetchall()]
            cursor3 = mysql.connection.cursor()
            sorgu3 = "select * from veli"
            cursor3.execute(sorgu3,)
            form.veli.choices = [(veli['veliid'],veli['veliadsoyad']) for veli in cursor3.fetchall()]
            
            return render_template("editogrenci.html", form = form)
        else:
            return render_template("index.html")
    else:
        form = OgrenciForm(request.form)
        newogrenciadsoyad = form.ogrenciadsoyad.data
        newogrenciyas = form.ogrenciyas.data
        newogrencitckn = form.ogrencitckn.data
        newveli = form.veli.data
        newsinif = form.sinif.data
        sorgu2 = "update ogrenci set ogrenciadsoyad = %s , ogrenciyas = %s ,ogrencitckn = %s, veliid = %s, sinifid = %s where ogrenciid = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(sorgu2,(newogrenciadsoyad,newogrenciyas,newogrencitckn,newveli,newsinif,id))
        mysql.connection.commit()
        return redirect(url_for("ogrenci"))

@app.route("/deleteogrenci/<string:id>")
@login_required
def deleteogrenci(id):
    cursor = mysql.connection.cursor()
    sorgu = "select * from ogrenci where ogrenciid = %s"
    result = cursor.execute(sorgu,(id,))
    if result >0:
        sorgu2 = "delete from ogrenci where ogrenciid = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("ogrenci"))
    else:
        return redirect(url_for("ogrenciid"))

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__=="__main__":
    sys.getdefaultencoding()
    app.run(debug=True)