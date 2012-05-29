# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'LocationPost.follower_notification_semaphore_processing'
        db.delete_column('custom_locationpost', 'follower_notification_semaphore_processing')

        # Deleting field 'LocationPost.follower_notification_status'
        db.delete_column('custom_locationpost', 'follower_notification_status')

        # Adding field 'LocationPost.water_quality_notification_email_daily_status'
        db.add_column('custom_locationpost', 'water_quality_notification_email_daily_status', self.gf('django.db.models.fields.SmallIntegerField')(default=0), keep_default=False)

        # Adding field 'LocationPost.water_quality_notification_email_daily_semaphore'
        db.add_column('custom_locationpost', 'water_quality_notification_email_daily_semaphore', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'LocationPost.water_quality_notification_email_immediate_status'
        db.add_column('custom_locationpost', 'water_quality_notification_email_immediate_status', self.gf('django.db.models.fields.SmallIntegerField')(default=0), keep_default=False)

        # Adding field 'LocationPost.water_quality_notification_email_immediate_semaphore'
        db.add_column('custom_locationpost', 'water_quality_notification_email_immediate_semaphore', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'LocationPost.water_quality_notification_email_weekly_status'
        db.add_column('custom_locationpost', 'water_quality_notification_email_weekly_status', self.gf('django.db.models.fields.SmallIntegerField')(default=0), keep_default=False)

        # Adding field 'LocationPost.water_quality_notification_email_weekly_semaphore'
        db.add_column('custom_locationpost', 'water_quality_notification_email_weekly_semaphore', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'LocationPost.water_quality_notification_mobile_status'
        db.add_column('custom_locationpost', 'water_quality_notification_mobile_status', self.gf('django.db.models.fields.SmallIntegerField')(default=0), keep_default=False)

        # Adding field 'LocationPost.water_quality_notification_mobile_semaphore'
        db.add_column('custom_locationpost', 'water_quality_notification_mobile_semaphore', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'LocationPost.follower_notification_semaphore_processing'
        db.add_column('custom_locationpost', 'follower_notification_semaphore_processing', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'LocationPost.follower_notification_status'
        db.add_column('custom_locationpost', 'follower_notification_status', self.gf('django.db.models.fields.SmallIntegerField')(default=0), keep_default=False)

        # Deleting field 'LocationPost.water_quality_notification_email_daily_status'
        db.delete_column('custom_locationpost', 'water_quality_notification_email_daily_status')

        # Deleting field 'LocationPost.water_quality_notification_email_daily_semaphore'
        db.delete_column('custom_locationpost', 'water_quality_notification_email_daily_semaphore')

        # Deleting field 'LocationPost.water_quality_notification_email_immediate_status'
        db.delete_column('custom_locationpost', 'water_quality_notification_email_immediate_status')

        # Deleting field 'LocationPost.water_quality_notification_email_immediate_semaphore'
        db.delete_column('custom_locationpost', 'water_quality_notification_email_immediate_semaphore')

        # Deleting field 'LocationPost.water_quality_notification_email_weekly_status'
        db.delete_column('custom_locationpost', 'water_quality_notification_email_weekly_status')

        # Deleting field 'LocationPost.water_quality_notification_email_weekly_semaphore'
        db.delete_column('custom_locationpost', 'water_quality_notification_email_weekly_semaphore')

        # Deleting field 'LocationPost.water_quality_notification_mobile_status'
        db.delete_column('custom_locationpost', 'water_quality_notification_mobile_status')

        # Deleting field 'LocationPost.water_quality_notification_mobile_semaphore'
        db.delete_column('custom_locationpost', 'water_quality_notification_mobile_semaphore')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'countries.country': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Country'},
            'iso': ('django.db.models.fields.CharField', [], {'max_length': '2', 'primary_key': 'True'}),
            'iso3': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'numcode': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'printable_name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'custom.community': {
            'Meta': {'object_name': 'Community'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'custom.location': {
            'Meta': {'object_name': 'Location'},
            'community': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['custom.Community']", 'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['countries.Country']", 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '26', 'decimal_places': '20', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '26', 'decimal_places': '20', 'blank': 'True'}),
            'published_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 5, 29, 15, 1, 10, 834497)'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'custom.locationpost': {
            'Meta': {'object_name': 'LocationPost'},
            'chlorine_level': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['custom.Location']"}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['custom.Provider']", 'null': 'True', 'blank': 'True'}),
            'published_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 5, 29, 15, 1, 10, 838696)'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'water_quality'", 'max_length': '100'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'water_quality_notification_email_daily_semaphore': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'water_quality_notification_email_daily_status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'water_quality_notification_email_immediate_semaphore': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'water_quality_notification_email_immediate_status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'water_quality_notification_email_weekly_semaphore': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'water_quality_notification_email_weekly_status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'water_quality_notification_mobile_semaphore': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'water_quality_notification_mobile_status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'water_source_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['custom.WaterSourceType']", 'null': 'True', 'blank': 'True'})
        },
        'custom.locationpostreporterremarks': {
            'Meta': {'object_name': 'LocationPostReporterRemarks'},
            'code': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'custom.locationsubscription': {
            'Meta': {'object_name': 'LocationSubscription'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email_subscription': ('django.db.models.fields.CharField', [], {'default': "'daily'", 'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['custom.Location']"}),
            'phone_subscription': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'custom.provider': {
            'Meta': {'object_name': 'Provider'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile_shorthand_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'custom.watersourcetype': {
            'Meta': {'object_name': 'WaterSourceType'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile_shorthand_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['custom']
