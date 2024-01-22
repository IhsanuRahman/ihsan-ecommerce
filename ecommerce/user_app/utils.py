from io import BytesIO
from .data import data
from .models import AdditionalImage, AdditionalInfo, Orders, Products,Category,SubCategory,ProductOptions, UserTemp,Cart
import random,datetime
from django.core.mail import send_mail
import urllib.request 
from PIL import Image 
import requests
import json
from django.core.files.base import ContentFile
import os
import datetime


def otp_generator(request,user,email=None):
    otp=random.randint(100000,999999)
    request.session['otp']=otp
    user=UserTemp.objects.get(id=user.id)
    user.stored_time=datetime.datetime.now()
    user.save()
    if user:
        if email is None:
            email=user.email
        send_mail(
        "verify ihsan account",
        f"your account is created and your verification code is {otp}.and note the link only valid until 3 minutes",
        "ihsanofficial.webservice@gmail.com",
        [email]
        )
        print(email)
    request.session['otp_datetime']=str(datetime.datetime.now())
    print(otp)


# def otp_generator_for_reset_pass(request):
#     otp=random.randint(100000,999999)
#     request.session['otp']=otp
#     user=UserModel.objects.filter(id=request.session['user_id']).first()
#     if user:
#         email=user.email
#         send_mail(
#         "verify movie gallery account",
#         f"your account is created and your verification code is {otp}.and note the link only valid until 3 minutes",
#         "moviegallerysite@gmail.com",
#         [email]
#         )
#     request.session['otp_datetime']=str(datetime.datetime.now())
#     print(otp)

def getImage():  
    return urllib.request.urlretrieve( 
  'https://media.geeksforgeeks.org/wp-content/uploads/20210318103632/gfg-300x300.png')
def otp_verify(request,otp):

    if request.session['otp']==otp:
        return True
    return False
    


def seeder():
    t=''
    l=[]
    tl=[]
    c=0
    k=1
    for i in data:
        if i=='\n':
            k+=1
        if i==",":
            tl.append(t)
            t=''
            c+=1
        if i!='\n' and i!=',':
            t+=i
        if i=='\n':
            tl.append(t)
            t=''
            l.append(tl)
            tl=[]
            c=0
    rc=0
    for li in l:
        rc+=1
        if rc>=50:
            api_key='1PNPWam7qbNUfNFzJnEWVBc4RqPxaL0OWoAA8GpOoLw'
        else:
            api_key='LGCw_6s6xp0qxCyoyxwmoqohq815BttWfrr2PqLYyk8'
        if len(li)>4:
            category=Category.objects.filter(name=li[3]).first()
            print(li)
            if not category:
                category=Category.objects.create(name=li[3])
                
                category.save()
                
            sub_category=SubCategory.objects.filter(parent_catogery=category,name=li[4]).first()
            if not sub_category:
                sub_category=SubCategory.objects.create(parent_catogery=category,name=li[4])
                
                sub_category.save()
            product=Products(title=li[1],brand=li[2],category=(category),sub_category=(sub_category),price=li[5],quantity=int(li[6]),gender=li[7])
            
            url=json.loads(requests.get(f'https://api.unsplash.com/search/photos?page=1&query={li[1]}&{li[3]}&client_id={api_key}').text)['results'][0]['urls']['raw']
            im=Image.open(requests.get(url, stream=True).raw)
            
            
            thumb_io = BytesIO()
            im=im.resize((450 , 720))
            im.save(thumb_io, "WEBP", quality=100)
            product.image.save(f'{product.pk}.webp', ContentFile(thumb_io.getvalue()), save=False)
            product.save()
            ds=li[8].split('|')
            print(ds) 
            product=Products.objects.filter(title=li[1]).first()
            for d in ds:
                splited=d.split(": ")
                print(splited[0])
                attrib=splited[0]
                value=splited[1]
                info=AdditionalInfo.objects.create(product=product,attribute=attrib,value=value)
                info.save()
            product.save()
            for i in range(1,4):
                additionalImage=AdditionalImage.objects.create(product=product)
                url=json.loads(requests.get(f'https://api.unsplash.com/search/photos?page=1&query={li[1]}&{li[3]}&client_id={api_key}').text)['results'][i]['urls']['raw']
                im=Image.open(requests.get(url, stream=True).raw)
                thumb_io = BytesIO()
                im=im.resize((450 , 720))
                im.save(thumb_io, "WEBP", quality=100)
                
                additionalImage.image.save(f'{product.pk}.webp', ContentFile(thumb_io.getvalue()), save=False)
                additionalImage.save()
            option=ProductOptions.objects.create(name=li[8])

            option.product.add(product)
            option.save()
    print('done')


def seederUpdate():
    pass

def clear():
    Cart.objects.all().delete()
    Orders.objects.all().delete()
    ProductOptions.objects.all().delete()
    SubCategory.objects.all().delete()
    Category.objects.all().delete()
    Products.objects.all().delete()