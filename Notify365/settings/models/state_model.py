from django.db import models

class State(models.Model):
    state = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=2)

    def __str__(self):
        return self.state