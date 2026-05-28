import datetime as dt

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Achievement, AchievementCat, Cat, CHOICES


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ('id', 'name')


class CatSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(many=True, required=False)
    color = serializers.ChoiceField(choices=CHOICES)
    age = serializers.SerializerMethodField()
    owner = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Cat
        fields = (
            'id', 'name', 'color', 'birth_year',
            'achievements', 'owner', 'age',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Cat.objects.all(),
                fields=('name', 'owner'),
                message='У вас уже есть котик с таким именем!'
            )
        ]

    def get_age(self, obj):
        return dt.date.today().year - obj.birth_year

    def validate_birth_year(self, value):
        year = dt.date.today().year
        if not (year - 40 < value <= year):
            raise serializers.ValidationError('Проверьте год рождения!')
        return value

    def validate(self, data):
        if 'color' in data and 'name' in data:
            if data['color'] == data['name']:
                raise serializers.ValidationError(
                    'Имя не может совпадать с цветом!')
        return data

    def create(self, validated_data):
        achievements_data = validated_data.pop('achievements', [])
        cat = Cat.objects.create(**validated_data)
        for achievement_data in achievements_data:
            achievement, _ = Achievement.objects.get_or_create(
                **achievement_data)
            AchievementCat.objects.create(
                achievement=achievement, cat=cat)
        return cat

    def update(self, instance, validated_data):
        achievements_data = validated_data.pop('achievements', None)
        instance = super().update(instance, validated_data)
        if achievements_data is not None:
            instance.achievements.clear()
            for achievement_data in achievements_data:
                achievement, _ = Achievement.objects.get_or_create(
                    **achievement_data)
                AchievementCat.objects.create(
                    achievement=achievement, cat=instance)
        return instance


class UserSerializer(serializers.ModelSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Cat._meta.get_field('owner').related_model
        fields = ('id', 'username', 'first_name', 'last_name', 'cats')
