from django.db import models
from colorfield.fields import ColorField


# Create your models here.
class Mission(models.Model):
    # our datastructure is defined here
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=65536)
    date = models.DateField()
    location = models.CharField(max_length=65536, null=True, blank=True)
    notes = models.CharField(max_length=65536, null=True, blank=True)

    class Meta:
        unique_together = ["name", "date"]

    # this function defines, what the value of print(mission) would be
    def __str__(self):
        return self.id


class File(models.Model):
    """The files table"""

    id = models.AutoField(primary_key=True)
    file = models.FileField(max_length=65536)
    video = models.FileField(blank=True, null=True, max_length=65536)
    robot = models.CharField(max_length=65536, null=True, blank=True)  # can be optional
    duration = models.BigIntegerField()  # unit: seconds
    size = models.BigIntegerField()  # unit: bytes


class Mission_files(models.Model):
    """The relationship table to connect Misson and File"""

    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    type = models.CharField(max_length=65536)  # either 'train' or 'test'


class Tag(models.Model):
    """The tags table"""

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=42, unique=True)
    color = ColorField(format="hex")

    def __str__(self):
        return f"id={self.id}, name='{self.name}', color={self.color}"


class Mission_tags(models.Model):
    """The relationship table to connect Misson and Tag"""

    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["mission", "tag"]


class Allowed_topic_names(models.Model):
    """A table to limit the allowed topic types"""

    name = models.CharField(primary_key=True)


class Topic(models.Model):
    """The topic table"""

    id = models.AutoField(primary_key=True)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    name = models.ForeignKey(Allowed_topic_names, on_delete=models.CASCADE)
    type = models.CharField()
    message_count = models.IntegerField()
    frequency = models.FloatField()

    class Meta:
        unique_together = ["file", "type", "name"]


"""
update db:
python manage.py makemigrations
python manage.py migrate

start server
python manage.py runserver
"""
