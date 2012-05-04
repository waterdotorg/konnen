# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Sms.message'
        db.alter_column('sms_sms', 'message', self.gf('django.db.models.fields.TextField')())


    def backwards(self, orm):
        
        # Changing field 'Sms.message'
        db.alter_column('sms_sms', 'message', self.gf('django.db.models.fields.TextField')(max_length=160))


    models = {
        'sms.sms': {
            'Meta': {'object_name': 'Sms'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_number': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'sent_date': ('django.db.models.fields.DateTimeField', [], {}),
            'to_number': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['sms']
