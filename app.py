from datetime import datetime
from flask import Flask ,render_template,request,redirect,send_file,flash
from flask_sqlalchemy import SQLAlchemy 
from werkzeug.utils import secure_filename
from flask_mail import Mail,  Message


mail = Mail()
app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scaler.sqlite3'
app.config['SECRET_KEY'] = '12345'
db = SQLAlchemy(app)

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_TLS= False,
    MAIL_USE_SSL=True,
    MAIL_USERNAME = 'parasmadan123@gmail.com',
    MAIL_PASSWORD = 'Paras555@'
)


mail.init_app(app)


class Interview(db.Model):                          # model for database 
    id = db.Column(db.Integer, primary_key=True)
    name_of_candidate=db.Column(db.String(30))      # Candidate Name
    email=db.Column(db.String(30))                  # Candidate email for informing him
    notes = db.Column(db.Text())                    # Notes for interviewer
    meeting_link=db.Column(db.String(50))           # Google meet or Zoom link
    resume_name = db.Column(db.String(20))          # Name of Resume of Candidate
    date_of_interview = db.Column(db.String(40), default=datetime.now)
    start_time=db.Column(db.String(25))             # Start time of Interview
    end_time=db.Column(db.String(25))               # End time of Interview
    status=db.Column(db.String(20))                 # Candidate avialable or not
    
db.create_all()


@app.route('/')             # home route 
def home():
    threads=Interview.query.order_by(Interview.id)
    return render_template('index.html',threads=threads)

# A function to convert time to suitable format for comparison  
def time_convert(p):
        d = datetime.strptime("22:30", "%H:%M")
        k=d.strftime("%I:%M")
        new=k.replace(":", ".")
        return float(new)       


@app.route('/add',methods=['GET', 'POST'])          # A route for scheduling new interview
def add():
    name=request.form['name']
    email=request.form['email']
    date=request.form['date']
    start_time=request.form['stime']
    end_time=request.form['etime']
    meeting_link=request.form['link']
    notes=request.form['notes']
    date=request.form['date']
    resume=request.files['file']
    
    
    
    # checking if there is another interview scheduled at that time 
    check=Interview.query.filter_by(name_of_candidate=name).first()
    if check != None and start_time !='' and end_time !='':
        if check.date_of_interview==date and time_convert(start_time) <= time_convert(check.start_time) <= time_convert(end_time):
            flash('There is an interview already scheduled for this candidate at this time. Please choose another time')
            return redirect('/')
        
        
        
    #setting values for default
    if resume.filename =='' :
        flash('Resume not provided')
        resume.filename='default.pdf'
    elif resume.filename !='':
        resume.save(secure_filename(resume.filename))
    if email == '':
        email='default@gmail.com'
        
    #pushing data into database
    candidate = Interview(name_of_candidate=name,email=email,notes=notes,date_of_interview=date,
                          meeting_link=meeting_link,
                          start_time=start_time,end_time=end_time,
                          resume_name=resume.filename,status='Available' )
    
    db.session.add(candidate)
    db.session.commit()
    body_message='Greetings from Scaler Academy! \n\nYour Interview is scheduled at '+str(start_time)+' on '+str(date)+'\n\nPlease join with the given meeting link. \n'+str(meeting_link)+'\nRegards\nParas From Scaler'
    msg = Message("Reminder for Interview",
                  sender="Scaler Academy",
                  recipients=[email],
                  body=body_message)
    mail.send(msg)
    return redirect('/')


@app.route('/download/<name>')                          # A route  for downloading resumes
def downloadFile (name):
    path = name
    return send_file(path, as_attachment=True)





@app.route('/delete/<id>/', methods = ['GET', 'POST'])  # A route for deleting interviews
def delete(id):
        my_data = Interview.query.get(id)
        db.session.delete(my_data)
        db.session.commit()
        return redirect('/')
    
    

@app.route('/update/<id>/', methods = ['GET', 'POST'])    # A route for updating the interview details 
def upd(id):
        my_data = Interview.query.get(id)
        my_data.name_of_candidate=request.form['name']
        my_data.email=request.form['email']
        my_data.date_of_interview=request.form['date']
        my_data.start_time=request.form['stime']
        my_data.end_time=request.form['etime']
        my_data.meeting_link=request.form['link']
        my_data.notes=request.form['notes']
        my_data.status=request.form['status']
        db.session.commit()
        return redirect('/')
    
if __name__ == '__main__':
	app.run()
    
    
    
