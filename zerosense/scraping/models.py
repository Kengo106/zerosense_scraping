from django.db import models
from datetime import date
import uuid
from django.utils import timezone


class Race(models.Model):

    class Meta:
        managed = False
        db_table = 'app1_race'
    race_name = models.CharField(max_length=255)
    rank = models.CharField(max_length=255)
    race_date = models.DateField(default=date.today)
    start_time = models.TimeField(default=timezone.now())
    is_votable = models.IntegerField(default=0)


class Horse(models.Model):

    class Meta:
        managed = False
        db_table = 'app1_horse'
    race = models.ForeignKey(Race, on_delete=models.CASCADE, null=True)
    horse_name = models.CharField(max_length=255)


class HorsePlace(models.Model):
    
    class Meta:
        managed = False
        db_table = 'app1_horsplase'
    horse = models.ForeignKey(Horse, on_delete=models.CASCADE)
    place = models.IntegerField(null=True)


class Odds(models.Model):
    
    class Meta:
        managed = False
        db_table = 'app1_horsplase'
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    tan = models.IntegerField(default=0)
    fuku_1 = models.IntegerField(default=0)
    fuku_2 = models.IntegerField(default=0)
    fuku_3 = models.IntegerField(default=0)
    umaren = models.IntegerField(default=0)
    umatan = models.IntegerField(default=0)
    wide_12 = models.IntegerField(default=0)
    wide_13 = models.IntegerField(default=0)
    wide_23 = models.IntegerField(default=0)
    trio = models.IntegerField(default=0)  # 三連複
    tierce = models.IntegerField(default=0)  # 3連単




# class User(models.Model):
#     uid = models.CharField(max_length=255)
#     username = models.CharField(max_length=255)


# class GameRule(models.Model):
#     start = models.DateField(default=date.today)
#     end = models.DateField(default=date.today)
#     open = models.BooleanField()
#     logic_id = models.IntegerField()


# class Game(models.Model):
#     game_rule = models.ForeignKey(
#         GameRule, on_delete=models.CASCADE, null=True)
#     name = models.CharField(max_length=255)
#     start_datetime = models.DateTimeField(auto_now_add=True)
#     id_for_serch = models.UUIDField(
#         default=uuid.uuid4,  editable=False)



# class GameComment(models.Model):
#     game = models.ForeignKey(Game, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     comment_text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)


# class Vote(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)
#     race = models.ForeignKey(Race, on_delete=models.CASCADE)
#     horse_first = models.ForeignKey(
#         Horse, on_delete=models.CASCADE, related_name='votes_first')
#     horse_second = models.ForeignKey(
#         Horse, on_delete=models.CASCADE, related_name='votes_second')
#     horse_third = models.ForeignKey(
#         Horse, on_delete=models.CASCADE, related_name='votes_third')
#     created_at = models.DateTimeField(auto_now_add=True)
#     comment = models.TextField(null=True)


# class GamePlayer(models.Model):
#     game = models.ForeignKey(Game, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)