# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'SmsControlTrans.created_date'
        db.add_column('sms_control_smscontroltrans', 'created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2012, 5, 11, 14, 16, 19, 900630), blank=True), keep_default=False)

        # Adding field 'SmsControlTrans.updated_date'
        db.add_column('sms_control_smscontroltrans', 'updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2012, 5, 11, 14, 16, 39, 320571), blank=True), keep_default=False)

        # Adding field 'SmsControlLocale.created_date'
        db.add_column('sms_control_smscontrollocale', 'created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2012, 5, 11, 14, 17, 0, 230564), blank=True), keep_default=False)

        # Adding field 'SmsControlLocale.updated_date'
        db.add_column('sms_control_smscontrollocale', 'updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2012, 5, 11, 14, 17, 9, 750565), blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'SmsControlTrans.created_date'
        db.delete_column('sms_control_smscontroltrans', 'created_date')

        # Deleting field 'SmsControlTrans.updated_date'
        db.delete_column('sms_control_smscontroltrans', 'updated_date')

        # Deleting field 'SmsControlLocale.created_date'
        db.delete_column('sms_control_smscontrollocale', 'created_date')

        # Deleting field 'SmsControlLocale.updated_date'
        db.delete_column('sms_control_smscontrollocale', 'updated_date')


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
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'sms_control.smscontroltrans': {
            'Meta': {'unique_together': "(('sms_control', 'sms_control_locale'),)", 'object_name': 'SmsControlTrans'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'help_text_trans': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phrase_trans': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '160'}),
            'sms_control': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms_control.SmsControl']"}),
            'sms_control_locale': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sms_control.SmsControlLocale']"}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['sms_control']
