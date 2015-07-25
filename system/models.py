from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Document(models.Model):
    '''
    status = { 
                in-warehouse,
                in-courier,
                destroyed,
                incorrect-input
             }
    location = {
                    storage 1
                    storage 2
                    storage 3
    }
    '''
    active = models.BooleanField(default = True)
    status = models.TextField()
    location = models.TextField()
    officeStartDate = models.DateField()
    centralManagementStartDate = models.DateField()
    archiveStartDate = models.DateField()
    
class Criterion(models.Model):
    documentID = models.ForeignKey(Document)
    criteriaType = models.TextField()
    criteriaValue = models.TextField()


class Requests(models.Model):
    '''
    protocolID has to be the autoincrement for every new bundle of requests, so there will be more documents in one paper protocol.
    status = {
                in-progress,
                accepted,
                verified,
                not-verified,
    }
    '''
    userID = models.ForeignKey(User)
    documentID = models.ForeignKey(Document)
    requestDate = models.DateField()
    status = models.TextField()
    fromLocation = models.TextField()
    toLocation = models.TextField()
    protocolID = models.IntegerField()

