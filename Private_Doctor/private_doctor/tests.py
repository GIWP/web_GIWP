from django.test import TestCase
from private_doctor.models import Doctor,Family,Appointment,Family_Doctor

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
