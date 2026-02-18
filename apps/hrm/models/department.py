class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    head = models.ForeignKey("hrm.Employee", null=True, blank=True, on_delete=models.SET_NULL)
