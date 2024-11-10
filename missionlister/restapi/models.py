from django.db import models


# Create your models here.
class Mission(models.Model):
    # our datastructure is defined here
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=65536)
    date = models.DateField()
    location = models.CharField(max_length=65536,null=True,blank=True)
    other = models.CharField(max_length=65536,null=True,blank=True)

    # this function defines, what the value of print(mission) would be
    def __str__(self):
        return self.id


class Tag(models.Model):
    '''The tags table'''
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=65536, unique=True)

class Mission_tags(models.Model):
    '''The relationship table to connect Misson and Tag'''
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
'''
update db:
python manage.py makemigrations
python manage.py migrate

start server
python manage.py runserver
'''