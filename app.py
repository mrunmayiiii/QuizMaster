from flask import Flask, render_template,redirect,request,session,flash,url_for
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime , date
from werkzeug.security import generate_password_hash  # Add this import
from werkzeug.security import check_password_hash
import seaborn as sns
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#orm means object relational mapping between python and database
#template inheritance
#session is like dictionary for security
# error codes
#crud create read update delete
#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
#pip freeze>requirements.txt
#pip install-r requirements.txt
curr_dir=os.path.dirname(os.path.abspath(__file__))
app=Flask(__name__,template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///quizmaster.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config["SECRET_KEY"]="mrunmai"
app.config["UPLOAD_FOLDER"] = os.path.join(curr_dir, "static","pics")

db=SQLAlchemy()
db.init_app(app)
app.app_context().push()

class UserAccount(db.Model):
    __tablename__="UserAccount"
    id=db.Column(db.Integer, primary_key=True)
    fullname=db.Column(db.String(80),nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password=db.Column(db.String(120),nullable=False)
    qualification=db.Column(db.String(120),nullable=False)
    dob=db.Column(db.String(120),nullable=False)
    is_admin=db.Column(db.Boolean,nullable=False,default=False)
    user_scores=db.relationship('UserScore',back_populates='user_account',cascade='all,delete-orphan')


class CourseTopic(db.Model):
    __tablename__="CourseTopic"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(80),nullable=False) 
    description=db.Column(db.String(120),nullable=False)
    course_sections=db.relationship("CourseSection", back_populates='course_topic',cascade="all,delete-orphan")

class CourseSection(db.Model):
    __tablename__="CourseSection"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(80),nullable=False) 
    description=db.Column(db.String(120),nullable=False)
    topic_id=db.Column(db.Integer, db.ForeignKey("CourseTopic.id"))
    course_topic=db.relationship("CourseTopic", back_populates='course_sections')
    quizzes=db.relationship("QuizTest",back_populates='course_section',cascade='all,delete-orphan')

class QuizTest(db.Model):
    __tablename__="QuizTest"
    id=db.Column(db.Integer, primary_key=True)
    date_ofquiz=db.Column(db.Date,nullable=False) 
    time_dur=db.Column(db.String(20),nullable=False)
    remarks=db.Column(db.String(120),nullable=False)
    section_id=db.Column(db.Integer, db.ForeignKey("CourseSection.id"),nullable=False)
    course_section=db.relationship("CourseSection", back_populates='quizzes')
    quiz_questions=db.relationship("QuizQuestion",back_populates='quiz_test',cascade='all,delete-orphan')
    user_scores=db.relationship('UserScore',back_populates='quiz_test',cascade='all,delete-orphan')

class QuizQuestion(db.Model):
    __tablename__="QuizQuestion"
    id=db.Column(db.Integer, primary_key=True)
    statement_que=db.Column(db.String(120),nullable=False)
    option1=db.Column(db.String(120),nullable=False)
    option2=db.Column(db.String(120),nullable=False)
    option3=db.Column(db.String(120),nullable=False)
    option4=db.Column(db.String(120),nullable=False)
    correction=db.Column(db.String(120),nullable=False)
    quiz_id=db.Column(db.Integer, db.ForeignKey("QuizTest.id"),nullable=False)
    quiz_test=db.relationship("QuizTest",back_populates='quiz_questions')

class UserScore(db.Model):
    __tablename__="UserScore"
    id=db.Column(db.Integer, primary_key=True)
    scores=db.Column(db.Integer,nullable=False) 
    user_id=db.Column(db.Integer, db.ForeignKey("UserAccount.id"))
    quiz_id=db.Column(db.Integer, db.ForeignKey("QuizTest.id"))
    timestamp=db.Column(db.DateTime,nullable=False)
    quiz_test=db.relationship('QuizTest',back_populates='user_scores')
    user_account=db.relationship('UserAccount',back_populates='user_scores')


def create_admin():
    admin_user=UserAccount.query.filter(UserAccount.email=="admin@gmail.com").first()
    if not admin_user:
        hashed_password = generate_password_hash("0000")
        admin=UserAccount(fullname="admin",email="admin@gmail.com",password=hashed_password,qualification="BS,iitm",dob="01-01-2000",is_admin=True)
        db.session.add(admin)
        db.session.commit()



db.create_all()
create_admin()


@app.route("/")
def hello_world():
    return redirect('/login')
    
@app.route("/login",methods=["POST", "GET"])
def login():
    if(request.method=="GET"):
        return render_template("login.html")
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]
        user=UserAccount.query.filter_by(email=email).first()

        if(user):            
            if check_password_hash(user.password, password):
                if(user.is_admin):
                    session["admin"]=user.id
                    # session["name"]=UserAccount.fullname
                    # session["is_admin"]=True
                    return redirect("/admin")
                else:
                    session["user"]=user.id
                    return redirect("/user")
            else:               
                flash("Invalid Password","error")
                return redirect("/login")
                
        else:
            flash("user not found","error")
            return redirect("/login")


#register route
@app.route("/register",methods=["POST", "GET"])
def register():
    if(request.method=="GET"):
        return render_template("register.html")
    if request.method=="POST":
        fullname=request.form["fullname"]
        email=request.form["email"]
        password=request.form["password"]
        qualification=request.form["qualification"]
        dob=request.form["dob"]
        hashed_password = generate_password_hash(password)
        user=UserAccount(fullname=fullname,email=email,password=hashed_password,qualification=qualification,dob=dob)
        db.session.add(user)
        db.session.commit()
        flash("User created successfully","success")
        return redirect("/login")



@app.route("/admin")
def adminpage():
    if 'admin' in session:
        topics=CourseTopic.query.all()
        scores=UserScore.query.all()
        print(topics)
        return render_template("admin.html",subjects=topics,scores=scores)
    return redirect("/login")

@app.route("/logout")
def logout():
    session.pop('admin')
    return redirect("/login")


@app.route("/logoutuser")
def logoutuser():
    session.pop('user')
    return redirect("/login")

@app.route("/showsubject/<int:subid>",methods=["POST", "GET"])
def showsubject(subid):
    if 'admin' in session:
        topic=CourseTopic.query.filter(subid==subid).first()
        sections=CourseSection.query.filter(subid==subid).all()
        return render_template("showsubject.html",subject=topic,chapter=sections)

@app.route("/showquiz/<int:quizid>",methods=["POST", "GET"])
def showquiz(quizid):
    if 'admin' in session:
        quiz=QuizTest.query.filter(quizid==quizid).first()
        questions=QuizQuestion.query.filter(quizid==quizid).all()
        return render_template("showquiz.html",quiz=quiz,questions=questions)

@app.route("/showchapter/<int:chapid>",methods=["POST", "GET"])
def showchapter(chapid):
    if 'admin' in session:
        section = CourseSection.query.filter_by(id=chapid).first()
        quizzes = QuizTest.query.filter_by(section_id=chapid).all()
        return render_template("showchapter.html",chapter=section,quiz=quizzes)

@app.route("/subject",methods=["POST", "GET"])
def subject():
    if 'admin' in session:
        if request.method=="POST":
            name=request.form["name"]
            description=request.form["description"]

            print("Form Data Received:", name, description)
            new_topic=CourseTopic(name=name,description=description)
            db.session.add(new_topic)
            db.session.commit()
            return redirect("/admin")
        else:
            return render_template("newsub.html")
    else:
        return redirect("/login")
            
@app.route("/editsubject/<int:subid>",methods=["POST", "GET"])
def editsubject(subid):
    if 'admin' in session:
        topic=CourseTopic.query.filter_by(id=subid).first()
        if not topic:
            return redirect("/admin")
        if request.method=="POST":
            name=request.form["name"]
            description=request.form["description"]
            topic.name=name
            topic.description=description
            db.session.commit()
            return redirect("/admin")
        else:
            return render_template("editsubject.html",subject=topic)
    else:
        return redirect("/login")
            
@app.route("/delsubject/<int:subid>", methods=["POST", "GET"])
def delsubject(subid):
    if 'admin' in session:
        topic=CourseTopic.query.filter_by(id=subid).first()
        if not topic:
            return redirect("/admin")
        if request.method=="POST":            
            db.session.delete(topic)
            db.session.commit()
            return redirect("/admin")
        return render_template("delpopup.html",subject=topic)
    return redirect("/login")
            

# CourseSection crud
@app.route("/chapter/<int:subid>",methods=["POST", "GET"])
def chapter(subid):
    if 'admin' in session:
        if request.method=="POST":
            name=request.form["name"]
            description=request.form["description"]

           
            section=CourseSection(name=name,description=description,topic_id=subid)
            db.session.add(section)
            db.session.commit()
            return redirect(url_for("showsubject",subid=subid))
        else:
            return render_template("chapternew.html",subid=subid)
    else:
        return redirect("/login")
    

@app.route("/editchapter/<int:chapid>",methods=["POST", "GET"])
def editchapter(chapid):
    if 'admin' in session:
        section=CourseSection.query.filter_by(id=chapid).first()
        subid=section.topic_id
        if not section:
            return redirect(url_for("adminpage"))
        
        subid=section.topic_id
        if request.method=="POST":
            name=request.form["name"]
            description=request.form["description"]
            
            section.name=name
            section.description=description
            db.session.commit()
            return redirect(url_for("showsubject",subid=subid))
        else:
            return render_template("editchapter.html",chapter=section)
    else:
        return redirect("/login")
    

@app.route("/delchapterpopup/<int:chapid>", methods=["POST", "GET"])
def delchapterpopup(chapid):
    if 'admin' in session:
        section=CourseSection.query.filter_by(id=chapid).first()
        if not section:
            return redirect('/admin')
        if request.method=="POST": 
            subid=section.topic_id           
            db.session.delete(section)
            db.session.commit()
            return redirect(url_for("showsubject",subid=subid))
        return render_template("delchapterpopup.html",chapter=section)
    return redirect("/login")


# quiz crud

@app.route("/quizcreate/<int:chapter_id>",methods=["POST", "GET"])
def quizcreate(chapter_id): 
    if 'admin' in session:
        if request.method=="POST":
            date_ofquiz=request.form["date_ofquiz"]
            time_dur=request.form["time_dur"]
            remarks=request.form["remarks"]
            dateofquiz=datetime.strptime(date_ofquiz, '%Y-%m-%d')
             
            quiz=QuizTest(date_ofquiz=dateofquiz,time_dur=time_dur,remarks=remarks,section_id=chapter_id)
            db.session.add(quiz)
            db.session.commit()
            return redirect(url_for("showchapter",chapid=chapter_id))
        else:
            return render_template("quiznew.html",chapter_id=chapter_id)
    else:
        return redirect("/login")

@app.route("/quizedit/<int:quizid>",methods=["POST", "GET"])
def quizedit(quizid): 
    if 'admin' in session:
        quiz=QuizTest.query.filter_by(id=quizid).first()
        if quiz:
            if request.method=="POST":
                date_ofquiz=request.form["date_ofquiz"]
                time_dur=request.form["time_dur"]
                remarks=request.form["remarks"]
                dateofquiz=datetime.strptime(date_ofquiz, '%Y-%m-%d')
                
                quiz.date_ofquiz= dateofquiz
                quiz.time_dur= time_dur
                quiz.remarks= remarks
               

                db.session.commit()
                return redirect(url_for("showchapter",chapid=quiz.section_id))
            else:
                return render_template("quizedit.html",quiz=quiz)
        else:
            return redirect("/admin")
    else:
        return redirect("/login")
    
@app.route("/delquizpopup/<int:quizid>", methods=["POST", "GET"])
def delquizpopup(quizid):
    if 'admin' in session:
        quiz=QuizTest.query.filter_by(id=quizid).first()
        if not quiz:
            return redirect('/admin')
        
        if request.method=="POST": 
            chapter_id=quiz.section_id         
            db.session.delete(quiz)
            db.session.commit()
            return redirect(url_for("showchapter",chapid=quiz.section_id))
        return render_template("delquizpopup.html",quiz=quiz)
    return redirect("/login")

#  Questions crud

@app.route("/questionmaking/<int:quizid>",methods=["POST", "GET"])
def questionmaking(quizid): 
    if 'admin' in session:
        if request.method=="POST":
            statement_que=request.form["statement_que"]
            option1=request.form["option1"]
            option2=request.form["option2"]
            option3=request.form["option3"]
            option4=request.form["option4"]
            correction=request.form["correction"]
            que=QuizQuestion(statement_que=statement_que,option1=option1,option2=option2,option3=option3,option4=option4,correction=correction,quiz_id=quizid)
            db.session.add(que)
            db.session.commit()
            return redirect(url_for("showquiz",quizid=quizid))
        else:
            return render_template("questionmaking.html",quizid=quizid)
    else:
        return redirect("/login")

@app.route("/queedit/<int:queid>",methods=["POST", "GET"])
def queedit(queid): 
    que=QuizQuestion.query.filter_by(id=queid).first()
    if 'admin' in session:
        if request.method=="POST":
            statement_que=request.form["statement_que"]
            option1=request.form["option1"]
            option2=request.form["option2"]
            option3=request.form["option3"]
            option4=request.form["option4"]
            correction=request.form["correction"]
             
            que.statement_que=statement_que
            que.option1=option1
            que.option2=option2
            que.option3=option3
            que.option4=option4
            que.correction=correction
          
       
            db.session.commit()
            return redirect(url_for("showquiz",quizid=que.quiz_test.id))
        else:
            return render_template("queedit.html",que=que)
    else:
        return redirect("/login")

@app.route("/delquepopup/<int:queid>", methods=["POST", "GET"])
def delquepopup(queid):
    if 'admin' in session:
        que=QuizQuestion.query.filter_by(id=queid).first()
        if not que:
            return redirect('/admin')
        
        if request.method=="POST": 
            quizid=que.quiz_test.id      
            db.session.delete(que)
            db.session.commit()
            return redirect(url_for("showquiz",quizid=quizid))
        return render_template("delquepopup.html",que=que)
    return redirect("/login")


#//user dashboard

@app.route("/user")
def userdash():
    if 'user' in session:
        quizzes=QuizTest.query.all()
        user=UserAccount.query.filter_by(id=session['user']).first()
        return render_template('userdash.html',quizes=quizzes,user=user)
    return redirect('/login')

#route to edit user profile details

@app.route("/userprofileedit", methods=["POST", "GET"])
def userprofileedit():
    if 'user' in session:
        user = UserAccount.query.filter_by(id=session['user']).first()
        
        if request.method == "POST":
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]

         
            existing_user = UserAccount.query.filter(UserAccount.email == email, UserAccount.id != user.id).first()
            if existing_user:
                flash("Email is already in use. Please choose a different one.", "danger")
                return redirect("/userprofileedit")

            user.fullname = name
            user.email = email
            user.password = generate_password_hash(password)

            db.session.commit()
            flash("Profile updated successfully", "success")
            return redirect("/user")

        return render_template("userprofileedit.html", user=user)
#//quiz taking routes

@app.route("/quizstart/<int:quizid>")
def quizstart(quizid):
    if 'user' in session:
        quiz = QuizTest.query.filter_by(id=quizid).first()
        questions=QuizQuestion.query.filter_by(quiz_id=quizid).all()
        if quiz.date_ofquiz < date.today():
            flash("Quiz not available ","danger")
            return redirect("/user")
        if len(questions)==0 :
            flash("No questions found","danger")
            return redirect("/user")
        session["timestamp"] = datetime.now().isoformat()
        user=UserAccount.query.filter_by(id=session['user']).first()
        return redirect("/quizrandom/"+str(quizid))
    return redirect('/login')

@app.route("/quizrandom/<int:quizid>")
def quizrandom(quizid):
    if "user" in session:
        quiz = QuizTest.query.filter_by(id=quizid).first()
        questions = QuizQuestion.query.filter_by(quiz_id=quizid).all()
        user = UserAccount.query.filter_by(id=session['user']).first()
       
        if "quiz_start_time" not in session:
            session["quiz_start_time"] = datetime.now().isoformat()
        
        return render_template("quizrandom.html", quiz=quiz, questions=questions, user=user)
    return redirect("/login")

@app.route("/quizsubmission/<int:quizid>", methods=["GET", "POST"])
def quizsubmission(quizid):
    if "user" in session:
        quiz = QuizTest.query.filter_by(id=quizid).first()
        questions = QuizQuestion.query.filter_by(quiz_id=quizid).all()
        user = UserAccount.query.filter_by(id=session['user']).first()
       
        if "quiz_start_time" in session:
            start_time = datetime.fromisoformat(session["quiz_start_time"])
            current_time = datetime.now()
            elapsed_minutes = (current_time - start_time).total_seconds() / 60
       
            session.pop("quiz_start_time", None)
            
            time_parts = quiz.time_dur.split(':')
            allowed_minutes = 0
            
            if len(time_parts) == 2:
                if time_parts[0].isdigit() and time_parts[1].isdigit():
                    allowed_minutes = int(time_parts[0]) * 60 + int(time_parts[1])
                elif time_parts[0].isdigit() and time_parts[1].isdigit():
                    allowed_minutes = int(time_parts[0]) + (int(time_parts[1]) / 60)
            
            if allowed_minutes > 0 and elapsed_minutes > allowed_minutes:
                finalscore = UserScore(scores=0, user_id=user.id, quiz_id=quizid, timestamp=datetime.now())
                db.session.add(finalscore)
                db.session.commit()
                flash("Time limit exceeded. Your quiz has been submitted with a score of 0.", "danger")
                return render_template("quizresult.html", score=0, quet=len(questions), user=user, time_exceeded=True)
        
        score = 0
        for q in questions:
            user_answer = request.form.get(str(q.id), "")
            correct_answer = q.correction.strip()
            if user_answer.strip().lower() == correct_answer.lower():
                score += 1
                
        finalscore = UserScore(scores=score, user_id=user.id, quiz_id=quizid, timestamp=datetime.now())
        db.session.add(finalscore)
        db.session.commit()
        
        return render_template("quizresult.html", score=score, quet=len(questions), user=user)
    return redirect("/login")

#creating prev route to show all the previous attempted quizes to user

@app.route("/user/prevquizes")
def prevquizes():
    if 'user' in session:
        user=UserAccount.query.filter_by(id=session['user']).first()
        scores=UserScore.query.filter_by(user_id=user.id).all()
        return render_template('prevquizes.html',scores=scores,user=user)
    return redirect('/login')

# route for admin search for user,subjects,chapters and quizes based on their names

@app.route("/adsearch", methods=["GET", "POST"])
def adsearch():
    if 'admin' in session:
        if request.method=="GET":
            search_query = request.args.get('search', '').strip()
            if not search_query:  
                return render_template("adsearch.html", users=[], subjects=[], chapters=[], quizes=[])
            print(f"Search Query: {search_query}")
            users=UserAccount.query.filter(UserAccount.fullname.ilike('%'+ search_query+'%')).all()
            subjects=CourseTopic.query.filter(CourseTopic.name.ilike('%'+ search_query+'%')).all()
            chapters=CourseSection.query.filter(CourseSection.name.ilike('%'+ search_query+'%')).all()
            quizes=QuizTest.query.filter(QuizTest.remarks.ilike('%'+ search_query+'%')).all()
            
            print("Users:", users)
            print("Subjects:", subjects)
            print("Chapters:", chapters)
            print("Quizzes:", quizes)
            
            return render_template("adsearch.html",users=users,subjects=subjects,chapters=chapters,quizes=quizes)
    return redirect("/login")

#creating a route for admin summary to show how no. of quizzes in each subject in bargraph and showing subject wise user attempts in pie chart

@app.route("/admin/summarypg")
def summarypg():
    if 'admin' in session:
        topics = CourseTopic.query.all()
        sections = CourseSection.query.all()
        users = UserAccount.query.all()

        chapcount = [(topic.name, CourseSection.query.filter_by(topic_id=topic.id).count()) for topic in topics]

        quizcount = [(section.name, QuizTest.query.filter_by(section_id=section.id).count()) for section in sections]

        quizsub = {topic.name: 0 for topic in topics}
        for topic in topics:
            topic_sections = CourseSection.query.filter_by(topic_id=topic.id).all()
            for section in topic_sections:
                quizsub[topic.name] += QuizTest.query.filter_by(section_id=section.id).count()  

        subnames = list(quizsub.keys())
        subvalues = list(quizsub.values())

        plt.figure(figsize=(7, 5))
        sns.barplot(x=subnames, y=subvalues)
        plt.title("Quiz Statistics")
        plt.xlabel("Topics")
        plt.ylabel("Number of Quizzes")
        plt.xticks(rotation=45)
        plt.savefig("static/pics/summary.png")
        plt.close()  

        usertries = {user.fullname: UserScore.query.filter_by(user_id=user.id).count() for user in users}

        trieduser = list(usertries.keys())
        triedvalues = list(usertries.values())

        if sum(triedvalues) > 0:
            plt.figure(figsize=(10, 10))
            plt.pie(triedvalues, labels=trieduser, autopct='%1.1f%%', shadow=True, startangle=90,pctdistance=0.85)
            plt.title("User Attempts")
            plt.savefig("static/pics/piechartsummary.png")
            plt.close()
        else:
            plt.figure(figsize=(7, 5))
            plt.text(0.5, 0.5, "No User Attempts", fontsize=12, ha='center', va='center')
            plt.axis('off')
            plt.savefig("static/pics/piechartsummary.png")
            plt.close()

        return render_template("summarypg.html", summary="static/pics/summary.png", piechartsummary="static/pics/piechartsummary.png")

    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)