# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Sms.semaphore_processing'
        db.add_column('sms_sms', 'semaphore_processing', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Sms.status_processing'
        db.add_column('sms_sms', 'status_processing', self.gf('django.db.models.fields.SmallIntegerField')(default=0), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Sms.semaphore_processing'
        db.delete_column('sms_sms', 'semaphore_processing')

        # Deleting field 'Sms.status_processing'
        db.delete_column('sms_sms', 'status_processing')


    models = {
        'sms.sms': {
            'Meta': {'object_name': 'Sms'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_number': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'semaphore_processing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sent_date': ('django.db.models.fields.DateTimeField', [], {}),
            'status_processing': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'to_number': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['sms']
