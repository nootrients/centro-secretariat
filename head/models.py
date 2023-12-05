from django.db import models

# Create your models here.
class YearlyScholarshipData(models.Model):
    year = models.PositiveIntegerField()
    semester = models.CharField(max_length=50)
    
    total_applications = models.PositiveIntegerField()
    total_accepted = models.PositiveIntegerField()
    total_rejected = models.PositiveIntegerField()
    
    total_new = models.PositiveIntegerField()
    total_renewing = models.PositiveIntegerField()
    total_graduates = models.PositiveIntegerField()
    
    total_basic_plus = models.PositiveIntegerField()
    total_basic_plus_new = models.PositiveIntegerField()
    total_basic_plus_renewing = models.PositiveIntegerField()
 
    total_basic_scholarship = models.PositiveIntegerField()
    total_basic_scholarship_new = models.PositiveIntegerField()
    total_basic_scholarship_renewing = models.PositiveIntegerField()
    
    total_suc_lcu = models.PositiveIntegerField()
    total_suc_lcu_new = models.PositiveIntegerField()
    total_suc_lcu_renewing = models.PositiveIntegerField()
    
    total_honors = models.PositiveIntegerField()
    total_honors_new = models.PositiveIntegerField()
    total_honors_renewing = models.PositiveIntegerField()
    
    total_premier = models.PositiveIntegerField()
    total_premier_new = models.PositiveIntegerField()
    total_premier_renewing = models.PositiveIntegerField()
    
    total_priority = models.PositiveIntegerField()
    total_priority_new = models.PositiveIntegerField()
    total_priority_renewing = models.PositiveIntegerField()