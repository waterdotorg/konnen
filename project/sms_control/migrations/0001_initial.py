# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SmsControl'
        db.create_table('sms_control_smscontrol', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phrase', self.gf('django.db.models.fields.CharField')(unique=True, max_length=160)),
            ('help_text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('sms_control', ['SmsControl'])

        # Adding model 'SmsControlLocale'
        db.create_table('sms_control_smscontrollocale', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('sms_control', ['SmsControlLocale'])

        # Adding model 'SmsControlTrans'
        db.create_table('sms_control_smscontroltrans', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sms_control', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sms_control.SmsControl'])),
            ('sms_control_locale', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sms_control.SmsControlLocale'])),
            ('phrase_trans', self.gf('django.db.models.fields.CharField')(unique=True, max_length=160)),
            ('help_text_trans', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('sms_control', ['SmsControlTrans'])

        # Adding unique constraint on 'SmsControlTrans', fields ['sms_control', 'sms_control_locale']
        db.create_unique('sms_control_smscontroltrans', ['sms_control_id', 'sms_control_locale_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'SmsControlTrans', fields ['sms_control', 'sms_control_locale']
        db.delete_unique('sms_control_smscontroltrans', ['sms_control_id', 'sms_control_locale_id'])

        # Deleting model 'SmsControl'
        db.delete_table('sms_control_smscontrol')

        # Deleting model 'SmsControlLocale'
        db.delete_table('sms_control_smscontrollocale')

        # Deleting model 'SmsControlTrans'
        db.delete_table('sms_control_smscontroltrans')


    models = {
        'sms_control.smscontrol': {
            'Meta': {'object_name': 'SmsControl'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phrase': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '160'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'sms_control.smscontrollocale': {
            'Meta': {'object_name': 'SmsControlLocale'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'sms_control.smscontroltrans': {
            'Meta': {'unique_together': "(('sms_control', 'sms_control_locale'),)", 'object_name': 'SmsControlTrans'},
            'help_text_trans': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phrase_trans': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '160'}),
            'sms_control': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms_control.SmsControl']"}),
            'sms_control_locale': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms_control.SmsControlLocale']"})
        }
    }

    complete_apps = ['sms_control']
