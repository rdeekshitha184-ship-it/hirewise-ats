from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate_name = models.CharField(max_length=100)
    email = models.EmailField()
    skills = models.TextField()
    experience_years = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(default=0.0)
    def __str__(self):
        return self.candidate_name