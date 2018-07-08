from __future__ import  print_function
from django.test import TestCase
from private_doctor.models import Doctor,Family,Appointment,Family_Doctor
import time
from functools import wraps
import requests,re,urlparse

def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        r = func(*args, **kwargs)
        end = time.time()
        print('{}.{}:{} seconds'.format(func.__module__, func.__name__, round(end - start, 2)))
        return r
    return wrapper

def test(test_name):
    def _test(func):
        @wraps(func)
        def __test(*args,**kwargs):
            print("test {0} begin:".format(test_name))
            func(*args,**kwargs)
            print("test {0} end\n".format(test_name))
        return __test
    return _test

class TaskBase(object):
    def __init__(self):
        self._request = requests

    @property
    def request(self):
        return self._request

    def run(self):
        pass

    @timeit
    def get(self, url, *args, **kwargs):
        print(url, end=" ")
        reply = self.request.get(url, *args, **kwargs)
        return reply

    @timeit
    def post(self, url, *args, **kwargs):
        print(url, end=" ")
        reply = self.request.post(url, *args, **kwargs)
        return reply

    def get_html(self, url):
        self.parse_html(self.get(url))

    def parse_html(self, reply):
        if not reply.url.endswith(("js", "css", "jpg")):
            resource = re.findall("(?<=\").*?\.js(?=\")", reply.text)
            resource += re.findall("(?<=src=\").*?\.jpg(?=\")", reply.text)
            resource += re.findall("(?<=href=\").*?\.css(?=\")", reply.text)
            for res in resource:
                self.get_html(urlparse.urljoin(reply.url, res))

class TaskSessionBase(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self._request = requests.session()

    def login(self):
        url = "http://127.0.0.1:8000/login/"
        data = {"username": "lmz", "password": "lmzlmz","identity":"female"}
        reply = self.post(url, data=data)
        return "errorCode" in reply and reply["errorCode"] == 0

    @test("Login")
    def run(self):
        self.login()
@timeit
def test_login():
    for i in range(1000):
        TaskSessionBase().run()

# Create your tests here.

class ModelTest(TestCase):
    def setUp(self):
        Doctor.objects.create(user='tzh',pwd='tzhtzh',sex='male',email='tzh@qq.com',
                              major='Psychiatric',text='Treatment of mental illness')
        Family.objects.create(user='wyj',pwd='wyjwyj',sex='male',email='wyj@qq.com',
                              text='I feel bad.',advice='Take medicine.')
        Appointment.objects.create(family=Family.objects.get(user='wyj'),
                                   doctor=Doctor.objects.get(user='tzh'),
                                   time='2018/07/05', response='accept')
        Family_Doctor.objects.create(family=Family.objects.get(user='wyj'),doctor_name='tzh')

    def test_doctor_models(self):
        result = Doctor.objects.get(user="tzh")
        self.assertEqual(result.email, "tzh@qq.com")
        self.assertEqual(result.major, "Psychiatric")

    def test_family_models(self):
        result = Family.objects.get(user="wyj")
        self.assertEqual(result.email, "wyj@qq.com")
        self.assertEqual(result.text, "I feel bad.")

    def test_appointment_models(self):
        result = Appointment.objects.get(family=Family.objects.get(user='wyj'))
        self.assertEqual(result.doctor, Doctor.objects.get(user='tzh'))
        self.assertEqual(result.time, "2018/07/05")

    def test_fd_models(self):
        result = Family_Doctor.objects.get(family=Family.objects.filter(user='wyj'))
        self.assertEqual(result.doctor_name, "tzh")


if __name__ == '__main__':
    test_login()
