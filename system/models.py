from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Files(models.Model):
    docfile = models.FileField(upload_to='files/%Y%m%d')

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
    officeStartDate = models.DateField(blank = True, null = True)
    centralManagementStartDate = models.DateField(blank = True, null = True)
    archiveStartDate = models.DateField(blank = True, null=True)
    userID = models.ForeignKey(User)
    fileID = models.ForeignKey(Files, blank=True, null=True)
    
class Criterion(models.Model):
    documentID = models.ForeignKey(Document)
    criteriaType = models.TextField()
    criteriaValue = models.TextField()


class Requests(models.Model):
    '''
    protocolID has to be the autoincrement 
    for every new bundle of requests, so 
    there will be more documents in one paper protocol.
    status = {
                in-progress,
                waiting-to-verify,
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


