from flask import Flask,render_template,request,redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta
import sqlite3
from sqlalchemy import desc, false


app = Flask(__name__)
# gone terminl and import app from flask then db.create_all()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'flask'
app.config["SESSION_PERMANENT"] = True

class News(db.Model):
    a = datetime.now()
    sno = db.Column(db.Integer, primary_key = True)  # one primary key is required to put in every db model
    title = db.Column(db.Text(50))
    desc = db.Column(db.Text(100))
    content = db.Column(db.Text(2000))
    imgholder = db.Column(db.Text(50))
    category = db.Column(db.Text(50))
    date = db.Column(db.Text, default = a.strftime(" %d/%B/%Y, %A ") )  #date is take here no need to mention anywhere else expect html page
    def __repr__(self):
        return f"{self.sno}. {self.title} {self.desc} {self.date} {self.content} "   # to format the way of displaying data

class Slider(db.Model):
    a = datetime.now()
    sno = db.Column(db.Integer, primary_key = True)  # one primary key is required to put in every db model
    title = db.Column(db.Text(50))
    desc = db.Column(db.Text(100)) 
    content = db.Column(db.Text(2000))
    imgholder = db.Column(db.Text(50))
    category = db.Column(db.Text(50))
    date = db.Column(db.Text, default = a.strftime(" %d/%B/%Y, %A ") )  #date is take here no need to mention anywhere else expect html page
    def __repr__(self):
        return f"{self.sno}. {self.title} {self.desc} {self.date} {self.content} "   # to format the way of displaying data


@app.route('/', methods=['GET'], defaults={"page": 1}) 
@app.route('/<int:page>', methods=['GET'])
def home(page):
     page = page
     data = News.query.order_by(desc(News.sno)).paginate(page=page,per_page=7)
     slider = Slider.query.all()
     return render_template('index.html',data=data,slider=slider)

@app.route('/newsmaker',methods=['GET','POST'],defaults={"page":1})
@app.route('/newsmaker/<int:page>', methods=['GET'])
def newsmaker(page):
    if session.get('name'):
        page = page 
        data = News.query.order_by(desc(News.sno)).paginate(page=page,per_page=7)
        return render_template('newsmaker.html',data = data)
    return redirect('/login')

#when user click on a specific news full fledged news will appear here

@app.route('/news/<string:title>',methods=['GET','POST'])
def news(title):
        currentdata = News.query.filter_by(title=title).first()
        data = News.query.order_by(desc(News.sno)).paginate(per_page=6)
        webtitle = "Other"
        return render_template("News.html",currentdata=currentdata,data=data,webtitle=webtitle)

@app.route('/Category/<string:category>', methods=['GET','POST'],defaults={'page':1})
@app.route('/category/<string:category>/<int:page>', methods=['GET'])
def category(category,page):
     page =page
     data = News.query.filter_by(category=category).order_by(desc(News.sno)).paginate(page=page,per_page=7)
     webtitle = category
     slider = Slider.query.all()
     return render_template("category.html",data = data,slider=slider,webtitle=webtitle)

@app.route('/Category/<string:category>/<string:title>')
def CurrentCategory(category,title):
    currentdata = News.query.filter_by(title=title).first()
    data = News.query.filter_by(category=category).order_by(desc(News.sno)).paginate(per_page=6)
    webtitle = category
    other_news = News.query.all() # to add aside new headlines
    return render_template("News.html",data = data,currentdata=currentdata,webtitle=webtitle,other_news=other_news)

#Crud funnction defined here

@app.route("/add",methods=['GET','POST'])  # to get (post and get  data) from html page
def add():
        if request.method == 'POST':
             title = request.form['title']  #data is getting from the html form of addblog.html
             desc = request.form['desc']
             content = request.form['content']
             imgholder = request.form['image']
             category = request.form['category']
             currentdate = datetime.now()
             date = currentdate.strftime("%d/%m/%Y, %A")
             record = News(title=title,desc=desc,content=content,imgholder=imgholder,category=category,date=date)
             db.session.add(record)
             db.session.commit()
             return redirect('/newsmaker')
        return render_template('addNews.html')

@app.route('/delete/<int:sno>')
def delete(sno):
         record = News.query.filter_by(sno=sno).first()
         db.session.delete(record)
         db.session.commit()
         return redirect('/newsmaker')

@app.route('/edit/<int:sno>',methods=['GET','POST'])
def edit(sno):
          data = News.query.get(sno)
          if request.method == 'POST':
              data.title = request.form['title']  #data is getting from the html form of addblog.html
              data.desc = request.form['desc']
              data.content = request.form['content']
              data.imgholder = request.form['image']
              data.category = request.form['category']
              db.session.commit()
              return redirect('/newsmaker')
          else:
              return render_template('edit.html',data=data)

# before deleting all news items it will first confirm
@app.route('/confirm')
def confirm():
    return render_template('confirm.html')

@app.route('/deleteall')
def deleteall():
        con = sqlite3.connect('news.db')
        cur = con.cursor()
        cur.execute('DELETE FROM News')
        con.commit()
        return redirect('/newsmaker')

#login section throgh which developer will do crud fucntions

@app.route('/login',methods=['POST',"GET"])
def login():
    myusername = "a"
    mypassword = "v"
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if (username == myusername and password == mypassword):
             session['name'] = myusername
             return redirect('/newsmaker')
        else:
            msg = "*username and password does not match*"
            return render_template("login.html", msg=msg)
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')

# to keep browser awy from storing cache for login.
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    print(response)
    return response

# image slider modifier
@app.route('/imgslider/<string:title>')
def imgslider(title):
    newImage = News.query.filter_by(title=title).first()
    Imgcategory = newImage.category
    OldImage = Slider.query.filter_by(category=Imgcategory).first()
    OldImage.title = newImage.title
    OldImage.desc = newImage.desc
    OldImage.content = newImage.content
    OldImage.imgholder = newImage.imgholder
    db.session.commit()
    return redirect('/newsmaker')


if __name__ == '__main__':
      app.run(debug=True)


