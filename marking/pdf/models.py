from django.db import models
import os
# Create your models here.


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return ext


def upload_pdf_path(instance, filename):
    # print(instance)
    # print(filename.name)
    new_filename = filename
    ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "uploaded_pdf/{final_filename}".format(final_filename=final_filename)

class Assessment(models.Model):
    teacher_id = models.IntegerField()
    file = models.FileField(upload_to=upload_pdf_path,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class meta:
        db_table = 'assessment'

class Question(models.Model):

    section_number = models.IntegerField()
    question_number = models.IntegerField()
    marks = models.IntegerField()
    question_text = models.CharField(max_length=500)
    marking_guide = models.TextField()
    assessment_id = models.ForeignKey(Assessment,on_delete=models.CASCADE)
    question_type = models.CharField(max_length=50,null=True,blank=True)
    model_answer = models.CharField(max_length=50,null=True,blank=True)
    topic = models.CharField(max_length=50,null=True,blank=True)
    learning_outcome = models.CharField(max_length=50,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class meta:
        db_table = 'questions'


class Attempts(models.Model):
    attempt_id = models.IntegerField()
    student_id = models.IntegerField()
    section_id = models.IntegerField()
    question_id = models.IntegerField()
    assessment = models.ForeignKey(Assessment,on_delete=models.CASCADE)
    answer = models.TextField()    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class meta:
        db_table = 'answers'