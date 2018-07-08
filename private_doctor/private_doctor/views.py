# coding: utf-8
from django.shortcuts import render
from django.shortcuts import HttpResponse, HttpResponseRedirect
from . import models
import json
from django.db.models import Count
from django.http import  JsonResponse
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
                return render(request, "fail_login.html")

        else:
            compare_user = models.Family.objects.filter(user=user, pwd=pwd)
            if compare_user:
                request.session['user'] = user
                request.session['pwd'] = pwd
                return HttpResponseRedirect('/thehomepage')
            else:
                return render(request, "fail_login.html")
    else:
            return render(request, "login.html")


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
                return render(request, "name_error.html")
        else:
            try:
                models.Family.objects.create(user=username, pwd=password,
                                             sex=sex, email=email)
                return HttpResponseRedirect('/login/')
            except:
                return render(request, "name_error.html")

    else:
        return render(request, 'register.html')


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
            password = request.POST.get("password", None)
            email = request.POST.get("email", None)
            major = request.POST.get("major", None)
            expert = request.POST.get("expert", None)
            models.Doctor.objects.filter(user=request.session['user'], pwd=request.session['pwd'])
            doctor = models.Doctor.objects.filter(user=request.session['user'])[0]
            models.Doctor.objects.filter(user=doctor.user).update(pwd=password, email=email, major=major, text=expert)
            return HttpResponseRedirect('/login')

        return render(request, "doctor_info.html")
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
                    text = request.POST.get(fd.family.user, None)
                    if text is not None:
                        family.advice=text
                        family.save()
            fds=models.Family_Doctor.objects.filter(doctor_name=doctor.user).all()
            return render(request, "manage.html", {"fds": fds})
        else:
            return render(request,"no_family.html")

    else:
        return HttpResponseRedirect('/login')


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
            return HttpResponseRedirect('/thehomepage/')
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


def search(request):
    if models.Family.objects.filter(user=request.session['user'],
                                   pwd=request.session['pwd']):
        # doctor_name=models.Family_Doctor.objects.filter(family__user=request.session['user'])[0].doctor_name
        family = models.Family.objects.filter(user=request.session['user'])
        df = models.Family_Doctor.objects.filter(family__user=request.session['user'])
        doctor_name = "暂无预约医生"

        if request.method == 'POST':
            major = request.POST.get("major", None)
            print("dedao" + major)
            request.session['major'] = major
            return HttpResponseRedirect('/result')
        else:

            if len(df) == 0:
                advice = "暂无医嘱"
            else:
                df = models.Family_Doctor.objects.filter(family__user=request.session['user'])[0]
                advice = family[0].advice
                doctor_name =  df.doctor_name

            hotmajors = models.Doctor.objects.values_list("major").annotate(hot_major_n=Count("major")).order_by(
                "hot_major_n")
            hotmajors = list(hotmajors)
            print(hotmajors[0][0])
            temp = []
            for k in hotmajors:
                temp.append(k[0])
            hotmajors = temp

            return render(request, "thehomepage.html", {"hotmajors": hotmajors,"doctor":doctor_name,"advice":advice})
    else:
       return HttpResponseRedirect('/login')





def searchlist(request):
    if request.method =="POST":
        doctor_select=request.POST.get("doctor_select",None)
        request.session['doctor_select']=doctor_select
        return HttpResponseRedirect("/doctor_view")
    else:
        major=request.session['major']

        doctor_list=models.Doctor.objects.filter(major=major)

        temp=[]
        for doc in doctor_list:
            temp.append(doc.user)
        doctor_list=temp

        return render(request,"result.html",{"doctorlist": json.dumps(doctor_list)})

def doctor_view(request):
    doctor_select=request.session["doctor_select"]
    doc=models.Doctor.objects.filter(user=doctor_select)
    print(doc[0].user)

    print(doc.all())
    return render(request, "doctor_view.html", {"doctor_name": doc[0].user,"doctor_email": doc[0].email,"doctor_expert": doc[0].major})

def home(request):
    return render(request,"home.html")
