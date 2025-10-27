from django.db import models

# Create your models here.

class DataInfo(models.Model):
    tips_id = models.CharField(max_length=13, primary_key=True)
    orders =  models.CharField(max_length=20)
    species = models.CharField(max_length=50)
    tax_id = models.CharField(max_length=20)
    basename = models.CharField(max_length=100)
    description =  models.TextField()
    display = models.BooleanField()
    class Meta:
        db_table = 'data_info'
        managed = False

class FileInfo(models.Model):
    tax_id = models.CharField(max_length=10, primary_key=True)
    size = models.CharField(max_length=30)
    count = models.CharField(max_length=10)
    filename = models.CharField(max_length=60, db_index=True)
    md5 = models.CharField(max_length=32)
    class Meta:
        db_table = 'file_info'
        managed = False
        indexes = [
            models.Index(fields=['filename'], name='idx_filename'),  # 显式定义索引
        ]

class TreeInfo(models.Model):
    tax_id = models.CharField(max_length=10, primary_key=True)
    tip_name = models.CharField(max_length=60)
    orders = models.CharField(max_length=20)
    kingdom = models.CharField(max_length=20)
    phylum = models.CharField(max_length=20)
    subphylum = models.CharField(max_length=20)
    class_name = models.CharField(max_length=20, db_column='class')
    subclass = models.CharField(max_length=20)
    infraclass = models.CharField(max_length=20)
    cohort = models.CharField(max_length=20)
    ncbi_order = models.CharField(max_length=20)
    suborder = models.CharField(max_length=40)
    infraorder = models.CharField(max_length=20)
    superfamily = models.CharField(max_length=20)
    family = models.CharField(max_length=40)
    subfamily = models.CharField(max_length=20)
    genus = models.CharField(max_length=20)
    species = models.CharField(max_length=60)
    class Meta:
        db_table = 'tree_info'
        managed = False
        indexes = [
            models.Index(fields=['tip_name'], name='idx_tip_name'),  # 显式定义索引
            models.Index(fields=['orders'], name='idx_orders'),
            models.Index(fields=['species'], name='idx_species'),
        ]