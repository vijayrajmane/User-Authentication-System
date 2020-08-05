from .models import Account
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    phoneNumber = PhoneNumberField()
    class Meta:
        model = Account
        fields = ['id', 'name', 'phoneNumber', 'email']

    def save(self):
        phoneNumber = self.validated_data['phoneNumber']
        account = Account.objects.filter(phoneNumber__iexact = str(phoneNumber))
        if account is None:
            raise serializers.ValidationError({'Phone number already exists'})
        else:
            user = Account(
                name = self.validated_data['name'],
                phoneNumber =str(phoneNumber) ,
                email = self.validated_data['email']
            )
            user.save()
            return user
