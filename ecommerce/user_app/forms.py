import datetime
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Address, OrderCancellDetials, Products, UserTemp,UserModel as User,UserModelOperation
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
import pytz
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import PasswordChangeForm



class LoginForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={'class':"form-control",'id':"username",'placeholder':"username" ,'style':"border-radius: 8px;border: 2px solid #D9D9D9;"}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class':"form-control",'id':"password",'placeholder':"password",'style':"border-radius: 8px;border: 2px solid #D9D9D9;"}))
    
    def is_valid(self) -> bool:
        valid=super().is_valid()
        username=self.cleaned_data.get('username')
        password=self.cleaned_data.get('password')
        user=User.objects.filter(username=username).first()
        if user is None or user.block:
            self.add_error('username','username doesn`t exist')
            return False    

        user=authenticate(username=username,password=password)
        if user is None:
            self.add_error('password','password not match')
            return False
        return user
    

class OTPForm(forms.Form):
    otp=forms.IntegerField(min_value=100000,max_value=999999,widget=forms.NumberInput(attrs={'class':"form-control",'placeholder':"otp" ,'style':"border-radius: 8px;border: 2px solid #D9D9D9;"}))


class RegisterForm(UserCreationForm):
    username=forms.CharField(widget=forms.TextInput(attrs={'class':"form-control",'id':"username",'placeholder':"username",'style':"border-radius: 8px;border: 2px solid #D9D9D9;"}))
    first_name=forms.CharField(widget=forms.TextInput(attrs={'class':"form-control  me-1",'id':"firstname",'placeholder':"firstname",'style':"border-radius: 8px;border: 2px solid #D9D9D9;"}))
    last_name=forms.CharField(widget=forms.TextInput(attrs={'class':"form-control  me-1",'id':"secondname",'placeholder':"secondname",'style':"border-radius: 8px;border: 2px solid #D9D9D9;"}))
    email=forms.EmailField(widget=forms.EmailInput(attrs={'class':"form-control",'id':"email",'placeholder':"email",'style':"border-radius: 8px;border: 2px solid #D9D9D9;"}))
    password1=forms.CharField(widget=forms.PasswordInput(attrs={'class':"form-control",'id':"password",'placeholder':"password",'style':"border-radius: 8px;border: 2px solid #D9D9D9;"}))
    password2=forms.CharField(widget=forms.PasswordInput(attrs={'class':"form-control",'id':"conform-password",'placeholder':"conform password",'style':"border-radius: 8px;border: 2px solid #D9D9D9;"}))
    
    def save(self, commit= True):
        username=self.cleaned_data.get('username')
        first_name=self.cleaned_data.get('first_name')
        last_name=self.cleaned_data.get('last_name')
        email=self.cleaned_data.get('email')
        password=self.cleaned_data.get('password1')

        user=UserModelOperation.objects.filter(user_model__username=username).first()
        same_emails=UserModelOperation.objects.filter(user_model__email=email)
        if user:  
            print(str(user.user_model.stored_time))
            
            if datetime.datetime.now().astimezone(tz=pytz.timezone('Asia/Kolkata'))-(user.user_model.stored_time.astimezone(tz=pytz.timezone('Asia/Kolkata')))>datetime.timedelta(minutes=3):
                user.delete()
                user=UserTemp.objects.create(username=username,first_name=first_name,last_name=last_name,email=email)
                user.password=make_password(password)
                operation=UserModelOperation.objects.create(operation='create',user_model=user)
                if commit:
                    operation.save()
                    user.save()
                    return user         
            else :
                print('user error')
                self.add_error('username','username is exist')
        elif same_emails:
            user=same_emails.first()
            
            if datetime.datetime.now().astimezone(tz=pytz.timezone('Asia/Kolkata'))-(user.user_model.stored_time.astimezone(tz=pytz.timezone('Asia/Kolkata')))>datetime.timedelta(minutes=3):
                user.delete()
                user=UserTemp.objects.create(username=username,first_name=first_name,last_name=last_name,email=email)
                user.password=make_password(password)
                operation=UserModelOperation.objects.create(operation='create',user_model=user)
                if commit:
                    operation.save()
                    user.save()
                    return user
                     
            else :
                print('user error')
                self.add_error('email','email is already in use') 
        elif User.objects.filter(email=email): 
            self.add_error('email','email is already in use') 
        else:
            
            user=UserTemp.objects.create(username=username,first_name=first_name,last_name=last_name,email=email)
            user.password=make_password(password)
            operation=UserModelOperation.objects.create(operation='create',user_model=user)
            if commit:
                operation.save()
                user.save()
                return user


class UserEditForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['username','first_name','last_name','email',]

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class':"form-control" ,'style':"border-radius: 8px;border: 2px solid #D9D9D9;"})

class PasswordEditForm(PasswordChangeForm):
    def __init__(self,user, *args, **kwargs):
        super().__init__(user,*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class':"form-control" ,'style':"border-radius: 8px;border: 2px solid #D9D9D9;"})

class ForgotPasswordForm(forms.Form):
    email=forms.EmailField(widget=forms.EmailInput(attrs={'class':"form-control",'id':"email",'placeholder':"email",'style':"border-radius: 8px;border: 2px solid #D9D9D9;"}))



class SortForm(forms.Form):
    sortby=forms.ChoiceField(choices=[('select','select'),('price','Price Low'),('-price','Price High')],widget=forms.Select(attrs={'id':"sortby",'class':"form-control"}))
    

class FilterForm(forms.Form):
    def __init__(self,categories, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for category in categories:
            self.fields[category.name]=forms.BooleanField(label=category.name,widget=forms.CheckboxInput(),required=False)

class BrandFilter(forms.Form):
    def __init__(self,products, *args, **kwargs):
        super().__init__(*args, **kwargs)
        brands=products.values_list('brand',flat=True).distinct()
        for brand in brands:
            self.fields[brand]=forms.BooleanField(label=brand,widget=forms.CheckboxInput(),required=False)
        


class PasswordResetForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class':"form-control" ,'style':"border-radius: 8px;border: 2px solid #D9D9D9;"})

        
class AddressForm(forms.ModelForm):
    def phone_number_validator(self,value):
        print('phone validator')
        if not (value>999999999 and value<10000000000):
            raise forms.ValidationError('enter a valid phone number')
    class Meta:
        model=Address
        exclude=['user']
        unique_together = ['user','holder_name','phone_number','country','address','pin_code','town_or_city','state','district']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class':"form-control" ,'style':"border-radius: 8px;border: 2px solid #D9D9D9;"})
        self.fields['phone_number'].validators=[self.phone_number_validator]

class CancelForm(forms.ModelForm):
    class Meta:
        model=OrderCancellDetials
        fields=['reason']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason'].widget.attrs.update({'class':"form-control" ,'style':"border-radius: 8px;border: 2px solid #D9D9D9;"})


            
            