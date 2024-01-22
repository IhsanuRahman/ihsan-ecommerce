import base64
from io import BytesIO,StringIO
from django import forms
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from PIL import Image 
from django.core.files.base import ContentFile
from user_app.models import AdditionalImage, Category, Coupons, OrderItem, Products, SubCategory,AdditionalInfo,ProductOptions,Orders

from django.contrib.auth.forms import UserChangeForm,UserCreationForm

class LoginForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={'class':"form-control",'id':"username"}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class':"form-control",'id':"password"}))
    
    def is_valid(self) -> bool:
        valid=super().is_valid()
        username=self.cleaned_data.get('username')
        password=self.cleaned_data.get('password')
        user=User.objects.filter(username=username).first()
        if user is None or not user.is_superuser:
            self.add_error('username','username doesn`t exist')
            return False

        user=authenticate(username=username,password=password)
        if user is None:
            self.add_error('password','password not match')
            return False
        return user
    


class ProductsForm(forms.ModelForm):
    options=forms.CharField(widget=forms.Textarea(),help_text="enter the options in line by line and seprate option type and option using `:` (eg:color:red)")
    additional_informations=forms.CharField(widget=forms.Textarea(),help_text="enter the information in line by line and seprate option type and option using `:` (eg:color:red)")
    additional_images=forms.ImageField()
    
    
    def save(self):
        product=super().save()
        info=self.cleaned_data['additional_informations'].split('\n')
        for i in info:
            spi=i.split(':')
            AdditionalInfo.objects.create(product=product,attribute=spi[0],value=spi[1]).save()
        options=self.cleaned_data['options'].split('\n')
        for i in options:
            op=ProductOptions.objects.create(name=i)
            op.product.add(product)
            op.save()
        return product
    
            

        
    class Meta:
        model=Products
        exclude=('is_deleted',) 


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['__all__'].widget.attrs.update({"class": "form-control"})
        # or iterate over field to add class for each field
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class':"form-control"})
        self.fields['additional_images'].widget.attrs.update({'multiple':"true",'id':'mulfile'})
        self.fields['price'].validators.append(MinValueValidator(1,'enter the minimum price'))


class ProductsUpdateForm(forms.ModelForm):
    options=forms.CharField(widget=forms.Textarea(),help_text="enter the options in line by line and seprate option type and option using `:` (eg:color:red)")
    additional_informations=forms.CharField(widget=forms.Textarea(),help_text="enter the information in line by line and seprate option type and option using `:` (eg:color:red)")
    additional_images=forms.ImageField()
    
    def save(self):
        product=super().save(commit=False)
        print(self.cleaned_data)
        if self.cleaned_data['title']:
            product.title=self.cleaned_data['title']
        if self.cleaned_data['brand']:
            product.brand=self.cleaned_data['brand']
        
        if self.cleaned_data['category']:
            product.category=self.cleaned_data['category']
                
                
        if self.cleaned_data['sub_category']:
            product.sub_category=self.cleaned_data['sub_category']
                
        if self.cleaned_data['price']:
            product.price=self.cleaned_data['price'] 
        if self.cleaned_data['quantity']:
            product.quantity=self.cleaned_data['quantity']
        if self.cleaned_data['gender']:
            product.gender=self.cleaned_data['gender']
        if self.cleaned_data['description']:
            product.description=self.cleaned_data['description']
        info=self.cleaned_data['additional_informations'].split('\n')
        AdditionalInfo.objects.filter(product__id=product.id).delete()
        for i in info:
            spi=i.split(':')
            AdditionalInfo.objects.create(product=product,attribute=spi[0],value=spi[1])
        options=self.cleaned_data['options'].split('\n')
        ProductOptions.objects.filter(product__id=product.id).delete()
        for i in options:
            
            op=ProductOptions.objects.create(name=i)
            op.product.add(product)
        print('save p')   
        product.save()
        return product
    
            

        
    class Meta:
        
        model=Products
        exclude=('is_deleted',) 
        


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['__all__'].widget.attrs.update({"class": "form-control"})
        # or iterate over field to add class for each field
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class':"form-control"})
        self.fields['additional_images'].widget.attrs.update({'multiple':"true"})
        self.fields['additional_images'].required=False
        self.fields['price'].validators.append(MinValueValidator(1,'enter the minimum price'))

class UserEditForm(UserChangeForm):
    wallet=forms.FloatField(min_value=0.0)
    block=forms.BooleanField(required=False)


class UserAddForm(UserCreationForm):
    block=forms.BooleanField(required=False)

class CategoryAddForm(forms.ModelForm):
    class Meta:
        model=Category
        exclude=('is_deleted',) 

class SubCategoryAddForm(forms.ModelForm):
    class Meta:
        model=SubCategory
        exclude=('is_deleted',) 


class OrderForm(forms.ModelForm):
    receive_datetime=forms.DateTimeField(required=False,widget=forms.DateTimeInput(attrs={'type':'datetime-local'}))
    class Meta:
        model=OrderItem
        fields=('__all__')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['__all__'].widget.attrs.update({"class": "form-control"})
        # or iterate over field to add class for each field
       
        for field in self.fields:
                self.fields[field].widget.attrs.update({'class':"form-control"})


class CouponsForm(forms.ModelForm):
    valid_till=forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type':'datetime-local'}),required=False)
    class Meta:
        model=Coupons
        exclude=['applied_users','is_expired']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['__all__'].widget.attrs.update({"class": "form-control"})
        # or iterate over field to add class for each field
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class':"form-control"})