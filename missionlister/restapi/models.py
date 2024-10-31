from django.db import models

# Create your models here.
class Mission(models.Model): 
    # our datastructure is defined here
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=65536) 
    date = models.DateTimeField()
    location = models.CharField(max_length=65536)
    other = models.CharField(max_length=65536)

    # this function defines, what the value of print(mission) would be
    def __str__(self):
        return self.id 