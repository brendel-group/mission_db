from django.db import models


# Create your models here.
class Mission(models.Model):
    # our datastructure is defined here
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=65536)
    date = models.DateField()
    location = models.CharField(max_length=65536)
    other = models.CharField(max_length=65536)

    # this function defines, what the value of print(mission) would be
    def __str__(self):
        return self.id


class Tag(models.Model):
    '''The tags table'''
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=65536)

class Mission_tags(models.Model):
    '''The relationship table to connect Misson and Tag'''
    mission_id = models.ForeignKey(Mission, on_delete=models.CASCADE)
    tag_id = models.ForeignKey(Tag, on_delete=models.CASCADE)
