
from django.shortcuts import render
from django.shortcuts import HttpResponse, HttpResponseRedirect
from . import models
import datetime
__author__ = 'Administrator'


def login(request):
    if request.method == 'POST':
        user = request.POST.get("username", None)
        pwd = request.POST.get("password", None)
        identity = request.POST.get("identity", None)
        if identity == "doctor":
            compare_user = models.Doctor.objects.filter(user=user, pwd=pwd)
            if compare_user:
                request.session['user'] = user
                request.session['pwd'] = pwd
                return HttpResponseRedirect('/doctor/')
            else:
                return render(request, "../templates/fail_login.html/")

        else:
            compare_user = models.Family.objects.filter(user=user, pwd=pwd)
            if compare_user:
                request.session['user'] = user
                request.session['pwd'] = pwd
                return HttpResponseRedirect('/family/')
            else:
                return render(request, "../templates/fail_login.html")
    else:
            return render(request, "templates/login.html")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username", None)
        password = request.POST.get("password", None)
        sex = request.POST.get("sex", None)
        email = request.POST.get("email", None)
        identity = request.POST.get("identity", None)
        if identity == "doctor":
            try:
                models.Doctor.objects.create(user=username, pwd=password,
                                             sex=sex, email=email)
                return HttpResponseRedirect('/login/')
            except:
                return render(request, "../templates/name_error.html")
        else:
            try:
                models.Family.objects.create(user=username, pwd=password,
                                             sex=sex, email=email)
                return HttpResponseRedirect('/login/')
            except:
                return render(request, "name_error.html")
            print("qusiba,feizhai")

    else:
        return render(request, '../templates/registration')

# def user(request):
#     if request.method=="POST":
#         username=request.POST.get("username", None)
#         password=request.POST.get("password", None)
#         sex=request.POST.get("sex", None)
#         email=request.POST.get("email", None)
#         models.UserInfo.objects.create(user=username,pwd=password,sex=sex,email=email)
#     userlist=models.UserInfo.objects.all()
#     return render(request, "user.html",{"data":userlist})


def doctor(request):
    if models.Doctor.objects.filter(user=request.session['user'],
                                    pwd=request.session['pwd']):
        df = models.Appointment.objects.filter(doctor__user=request.session['user'],response="successful").all()
        families = []
        for record in df:
            family = get_family(record.family.user,families)
            if family is not False:
                family['times'].append(record.time)
            else:
                families.append({'user': record.family.user,
                                 'times': [record.time]})
        messages = models.Appointment.objects.filter(doctor__user=request.session['user'], response='waiting').all()
        data = {
            "families": families,
            "messages": messages
        }
        if request.method=='POST':
            f=request.POST.get("family",None)
            t=request.POST.get("time",None)
            a=models.Appointment.objects.filter(family__user=f,time=t,doctor__user=request.session['user'])[0]
            if request.POST.get("act",None)=="accept":
                a.response="successful"
            else:
                a.response="failed"
            a.save()
        return render(request, 'doctor.html', data)
    else:
        return HttpResponseRedirect('/login')


def get_family(user, families):
    print(families)
    for family in families:
        if family['user'] == user:
            return family
    return False


def family(request):
    if models.Family.objects.filter(user=request.session['user'],
                                   pwd=request.session['pwd']):
        doctor_name=models.Family_Doctor.objects.filter(family__user=request.session['user'])[0].doctor_name
        family = models.Family.objects.filter(user=request.session['user'])
        df = models.Family_Doctor.objects.filter(family__user=request.session['user'],doctor_name=doctor_name)
        if len(df) == 0:
            return HttpResponseRedirect('/choice/')
        else:
            df =  models.Family_Doctor.objects.filter(family__user=request.session['user'])[0]
            advice = family[0].advice
            return render(request, 'family.html',{"doctor":df.doctor_name,"advice":advice})
    else:
       return HttpResponseRedirect('/login')


def fail_login(request):
    return render(request, "fail_login.html")


def doctor_info(request):
    if models.Doctor.objects.filter(user=request.session['user'],
                                    pwd=request.session['pwd']):
        doctor = models.Doctor.objects.filter(user=request.session['user'])[0]
        if request.method == "POST":
            text = request.POST.get("desc", None)
            doctor.text=text
            doctor.save()
        desc = doctor.text
        return render(request, "doctor_info.html", {"desc": desc})
    else:
        return HttpResponseRedirect('/login')


def manage(request):
    if models.Doctor.objects.filter(user=request.session['user'],
                                    pwd=request.session['pwd']):
        doctor = models.Doctor.objects.filter(user=request.session['user'])[0]
        fds = models.Family_Doctor.objects.filter(doctor_name=doctor.user).all()
        if fds:
            for fd in fds:
                family = models.Family.objects.filter(user = fd.family.user)[0]
                if request.method == "POST":
                    text = request.POST.get("desc", None)
                    family.advice=text
                    family.save()
                return render(request, "manage.html", {"fds": fds,"advice":family.advice})
        else:
            return render(request,"no_family.html")
    else:
        return HttpResponseRedirect('/login')


def test(request):
    print(request.POST)
    data = {
        'messages': [{
            'time': 'asdas',
            'family': 'asdhjkqwhjek'
        }]
    }
    return render(request, "doctor.html", data)

def choice(request):
    if models.Family.objects.filter(user=request.session['user'],
                                        pwd=request.session['pwd']):
        doctors=models.Doctor.objects.all()
        if request.method=="POST":
            user = request.POST.get("user",None)
            family=models.Family.objects.filter(user=request.session['user'])[0]
            fd = models.Family_Doctor.objects.filter(family__user=family.user)
            if len(fd)==0:
                models.Family_Doctor.objects.create(doctor_name=user,family=family)
            else:
                if fd[0].doctor_name!=user:
                    fd[0].doctor_name=user
                    fd[0].save()
                    family.advice="暂无"
                    family.save()
            return HttpResponseRedirect('/family/')
        return render(request,"choice.html",{"doctors":doctors})
    else:
        return HttpResponseRedirect('/login/')

def appointment(request):
    if models.Family.objects.filter(user=request.session['user'],
                                    pwd=request.session['pwd']):
        family = models.Family_Doctor.objects.filter(family__user=request.session['user'])
        if len(family)==0:
                return HttpResponseRedirect('/choice')
        else:
            if request.method == "POST":
                date=request.POST.get("date",None)
                doctor_name=family[0].doctor_name
                doctor=models.Doctor.objects.filter(user=doctor_name)[0]
                Family=models.Family.objects.filter(user=request.session['user'])[0]
                response=request.POST.get("response","waiting")
                appointment= models.Appointment.objects.filter(family=Family,doctor=doctor,time=date)
                if appointment:
                    appointmentlist=models.Appointment.objects.filter(family__user=request.session['user'],doctor__user=doctor_name).all()
                    return render(request,"appointment.html",{"appointments":appointmentlist})
                else:
                    models.Appointment.objects.create(family=Family,doctor=doctor,time=date,response=response)
                    appointmentlist=models.Appointment.objects.filter(family__user=request.session['user'],doctor__user=doctor_name).all()
                    return render(request,"appointment.html",{"appointments":appointmentlist})
            else:
                doctor_name=family[0].doctor_name
                appointmentlist=models.Appointment.objects.filter(family__user=request.session['user'],doctor__user=doctor_name).all()
                return render(request,"appointment.html",{"appointments":appointmentlist})
    else:
        return HttpResponseRedirect('/login')

def history(request):
    if models.Family.objects.filter(user=request.session['user'],
                                    pwd=request.session['pwd']):
        family = models.Family.objects.filter(user=request.session['user'])[0]
        if request.method == "POST":
            text = request.POST.get("desc", None)
            family.text=text
            family.save()
        desc = family.text
        return render(request, "history.html", {"desc": desc})
    else:
        return HttpResponseRedirect('/login')