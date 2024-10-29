from django.db import models

# Create your models here.
class Mission(models.Model): 
    # our datastructure is defined here
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=1000) # TODO: what should max_length be?
    date = models.DateTimeField()
    location = models.CharField(max_length=1000)
    other = models.CharField(max_length=1000)

    # this function defines, what the value of print(mission) would be
    def __str__(self):
        return self.id # TODO: id or name?