from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.core.mail import send_mail
from django.conf import settings

from .serializers import UserSerializer
from .models import Account
import random
from phonenumber_field.phonenumber import PhoneNumber
from twilio.rest import Client


from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.renderers import TemplateHTMLRenderer
# Create your views here.

otp = {}    # Dict to save otp w.r.t there phone Number

def registerPage(request):
    
    return render(request, 'user/register.html')

def index(request):
    global otp
    print(otp)

    if request.user.is_authenticated:
        user = Account.objects.filter(phoneNumber = str(request.user) )
        context = {
            'details': user
        }
        return render(request, 'user/login.html', context)
    else:
        return render(request, 'user/login.html')


# Verify Contact details while creating new account
@api_view(['POST'])
def registerVerify(request):
        if request.method == "POST":
            print(request.data)
            print(request.data.get('phoneNumber'))
            phone = request.data.get('phoneNumber')
            email = request.data.get('email')
            data = {}
            user = Account.objects.filter(phoneNumber = phone)  # Check if user already exists or not

            if user.exists():                                   # if exists pass error
                data['response'] = 'fail'
                data['message'] = 'Phone Number already registered'
                print('Phone Number already registered')
                return Response(data)

            else:                                           # else generate otp 
                key = generateOTP(phone)                    # phone number OTP using generateOTP()
                key2 = generateOTP(phone)                   # email OTP using generateOTP()
                email_flag = sendEmailOTP(email, key2)      # Send OTP through email
                if key is not None:
                    global otp
                    print(len(otp))
                    otp[phone] = key 
                    otp[email] = key2       # save otp w.r.t its phone Number
                    print(otp)
                    flag = sendOTP(phone, key)         # Send OTP through Phone Number using sendOTP() and set flag
                    if flag:                            # if flag = true return json response success

                        data['response'] = 'success'
                        return Response(data)
                    else:                               # else return json response fail
                        print('Sending Failed')
                        data['response'] = 'fail'
                        return Response(data)
                else:
                    print('OTP generation failed')
                    return Response({'error: OTP generation failed'})



# Register user after entering OTP
@api_view(['POST', 'GET'])
def register(request,format=None):
    if request.method == "POST":
        print(request.data)
        # if OTP from local dictionary matches with otp entered in form then save user
        if otp[request.data.get('phoneNumber')] == int(request.data.get('otp')) and otp[request.data.get('email')] == int(request.data.get('emailotp')):
            
            account = Account(
                name = request.data.get('name'),
                phoneNumber = request.data.get('phoneNumber'),
                email = request.data.get('email')
            )
            account.save()
            account.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, account)                             # After saving user login with same user
            del otp[request.data.get('phoneNumber')]
            del otp[request.data.get('email')]
            data = {}
            data['response'] = 'success'

            ''' 
            Problem in django-phonenumber-field package so registering using above method.
            Otherwise we can use Django Rest Framework method which is by using serializer
            which is shown below 

            '''
            # serializer = UserSerializer(data=request.data)
            # data = {}
            # if serializer.is_valid():
            #     account = serializer.save()
            #     data['response'] = 'success'
            #     data['phoneNumber'] = account.phoneNumber
            #     data['email'] = account.email
            #     # user = Account.objects.get(phoneNumber =str(account.phoneNumber) )
            #     # user.backend = 'django.contrib.auth.backends.ModelBackend'
            #     # login(request, user)
            
            # else:
            #     data = serializer.errors
            # return Response(data)

            return Response(data)


    # Get all user 
    elif request.method == 'GET':
        try:
            item = Account.objects.all()
        except Account.DoesNotExist:
            raise Response(status=404)
        serializer = UserSerializer(item, many=True)
        return Response(serializer.data)


# Send OTP while Login 
@api_view(['POST'])
def validateContact(request):
        if request.method == "POST":
            print(request.data)
            print(request.data.get('phoneNumber'))
            phone = request.data.get('phoneNumber')
            data = {}
            user = Account.objects.filter(phoneNumber = phone)  # check if user exists
            print('@@@@')
            print(user)
            if user.exists():               #if exists genetrate OTP
                key = generateOTP(phone)
                global otp
                print(len(otp))
                otp[phone] = key
                print(otp)
                flag = sendOTP(phone, key)
                if flag:

                    data['response'] = 'success'
                    return Response(data)
                else:
                    pass
            
            else:
                data['response'] = 'fail'
                data['message'] = 'Phone Number not registered'
                return Response(data)

def generateOTP(phone):
    if phone:
        key = random.randint(999, 9999)
        print(key)
        return key

# Login user after entering login OTP  
@api_view(['POST'])
def signin(request,format=None):
    if request.method == 'POST':
        global otp

        otpS = otp[request.data.get('phoneNumber')]
        password = int(request.data.get('otp'))

        # if OTP from local dictionary matches with otp entered in form then save user
        if otp[request.data.get('phoneNumber')] == int(request.data.get('otp')):
            user = Account.objects.get(phoneNumber =str(request.data.get('phoneNumber')) )
            print(user)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)                        # login user

            del otp[request.data.get('phoneNumber')]      # delete otp from local dict
            data ={}
            data['response'] = 'success'

            return Response(data)
            # if user is not None:

            #     login(request,user)
            #     del otp[request.data.get('phoneNumber')]
            #     print('SUCCESSSSSSSSS')
            #     return Response({
            #         'success': True
            #     })
            # else:
            #     print('FAIL')
            #     return Response({
            #         'success': False
            #     })
        else:

            return Response('Enter Valid OTP')


# Sending OTP using 3rd party service called twilio 
# https://www.twilio.com/
# create account on above link to use service
# from twilio.rest import Client <- import this before using
def sendOTP(phone, key):
    if phone is not None:

        # twilio provide account_sid, auth_token, my_twilio
        account_sid = '<your account sid>'
        auth_token = '<your auth token>'
        my_twilio = '<your trial number>'          # from where message is send 


        client = Client(account_sid, auth_token)
 

        message =  client.messages.create(
            to = phone,
            from_=my_twilio,
            body = 'Your Auth system verification OTP is '+str(key) # message body
        )
        print(message)
        return True

def sendEmailOTP(email, key2):

    '''
    Turn on less secure app access in host email account to send the message.
    You can use temporary mail service to check mail
    '''

    # check settings.py for some setting
    if email:
        print(email)
        subject = 'Auth sys email verification'
        message = 'Your email verification OTP is '+ str(key2)
        from_email = settings.EMAIL_HOST_USER
        to_list = [email]
        
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        print('Mail send')
        return True

# Logout from session
def logout_view(request):
    logout(request)
    return redirect('/')