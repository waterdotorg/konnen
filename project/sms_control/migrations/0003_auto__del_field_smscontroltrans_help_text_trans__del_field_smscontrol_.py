# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'SmsControlTrans.help_text_trans'
        db.delete_column('sms_control_smscontroltrans', 'help_text_trans')

        # Deleting field 'SmsControl.help_text'
        db.delete_column('sms_control_smscontrol', 'help_text')


    def backwards(self, orm):
        
        # Adding field 'SmsControlTrans.help_text_trans'
        db.add_column('sms_control_smscontroltrans', 'help_text_trans', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)

        # Adding field 'SmsControl.help_text'
        db.add_column('sms_control_smscontrol', 'help_text', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)


    models = {
        'sms_control.smscontrol': {
            'Meta': {'object_name': 'SmsControl'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phrase': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '160'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'sms_control.smscontrollocale': {
            'Meta': {'object_name': 'SmsControlLocale'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'sms_control.smscontroltrans': {
            'Meta': {'unique_together': "(('sms_control', 'sms_control_locale'),)", 'object_name': 'SmsControlTrans'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phrase_trans': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '160'}),
            'sms_control': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms_control.SmsControl']"}),
            'sms_control_locale': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms_control.SmsControlLocale']"}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['sms_control']
