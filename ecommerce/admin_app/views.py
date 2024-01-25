from io import BytesIO
import os
from PIL import Image
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_control
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from json import dumps
from django.core.files.base import ContentFile
from user_app.models import AdditionalImage, AdditionalInfo, Coupons, OrderItem, Orders, ProductOptions, Products, SubCategory, UserModel
from .models import Sales
from .forms import CategoryAddForm, CouponsForm, LoginForm, OrderForm, ProductsForm, ProductsUpdateForm, SubCategoryAddForm, UserEditForm,Category
from django.contrib.auth.forms import SetPasswordForm
from django.db.models import Sum
from django.contrib import messages


def super_user_check(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('home')
        return func(request, *args, **kwargs)
    return wrapper


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def home(request):
    if not request.user.is_superuser:
        return redirect('')
    if request.POST.get('report_mode',False):
        mode=request.POST.get('report_mode')
        if mode == 'monthly':
            print('home')
            sales=Sales.objects.values('date__month').annotate(total_money = Sum('total_money'))
            dates=[(date[0]) for date in sales.values_list('date__month')]
            sales_dates=dumps(dates)
            sales_money=dumps([sale[0] for sale in sales.values_list('total_money')])
            salesmoney=[sale[0] for sale in sales.values_list('total_money')]
            data=dumps(list(zip(dates,salesmoney)))
            sales=Sales.objects.all()
        elif mode == 'yearly':
            sales=Sales.objects.values('date__year').annotate(total_money = Sum('total_money'))
            dates=[(date[0]) for date in sales.values_list('date__year')]
            sales_dates=dumps(dates)
            sales_money=dumps([sale[0] for sale in sales.values_list('total_money')])
            salesmoney=[sale[0] for sale in sales.values_list('total_money')]
            data=dumps(list(zip(dates,salesmoney)))
            sales=Sales.objects.all()
    else:
        sales=Sales.objects.all()
        dates=[(date[0].strftime('%Y/%m/%d')) for date in sales.values_list('date')]
        sales_dates=dumps(dates)
        sales_money=dumps([sale[0] for sale in sales.values_list('total_money')])
        salesmoney=[sale[0] for sale in sales.values_list('total_money')]
        data=dumps(list(zip(dates,salesmoney)))
        print(data)
    max_sale=0
    if sales.values_list('total_money'):
        max_sale=max(round(max(sales.values_list('total_money'))[0],-2),round(max(sales.values_list('total_money'))[0]))
    return render(request,'admin/index.html',{'sales':sales,'sales_dates':sales_dates,'sales_money':sales_money,'max_sale':max_sale,'data':data})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def products(request):
    products=Products.objects.all()
    return render(request,'admin/products.html',{'products':products})
    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def add_product(request):
    print('add page')
    form=ProductsForm
    if request.POST:
        form=ProductsForm(request.POST,request.FILES)
        if form.is_valid():
            print('valid')
            product=form.save()
            images=request.FILES.getlist('additional_images')
            for image in images:
                additionalImage=AdditionalImage.objects.create(product=product)
                im=Image.open(image)
                thumb_io = BytesIO()
                im.save(thumb_io, im.format, quality=100)
                additionalImage.image.save(f'{product.id}.{im.format}', ContentFile(thumb_io.getvalue()), save=False)
                additionalImage.save()
            return redirect(f'/admin/product/{product.id}')
    return render(request,'admin/product_add.html',{'form':form})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def product_page(request,id):
    try:
        product=Products.objects.get(id=id)
    except :
        return redirect('/admin')
    additional_information=AdditionalInfo.objects.filter(product=product)
    info=''
    for i in additional_information:
        info=info+f"{i.attribute}:{i.value}\n"
    additional_images=(AdditionalImage.objects.filter(product=product))
    print(product)
    product_options=ProductOptions.objects.filter(product=product)
    options=''
    for op in product_options:
        options=options+f'{op.name}\n'

    data={'additional_informations':info,'additional_images':additional_images,'options':options}
    form=ProductsUpdateForm(instance=product,initial=data)
    if request.POST:
        form=ProductsUpdateForm(request.POST,request.FILES,instance=product)
        if form.is_valid():
            product=form.save()
            if request.FILES.get('image'):
                im=Image.open(request.FILES.get('image'))
                thumb_io = BytesIO()
                im.save(thumb_io, im.format, quality=100)
                product.image.save(f'{product.id}.{im.format}', ContentFile(thumb_io.getvalue()), save=False)
                product.save()
            images=request.FILES.getlist('additional_images')
            for image in images:
                additionalImage=AdditionalImage.objects.create(product=product)
                im=Image.open(image)
                thumb_io = BytesIO()
                im.save(thumb_io, im.format, quality=100)
                additionalImage.image.save(f'{product.id}.{im.format}', ContentFile(thumb_io.getvalue()), save=False)
                additionalImage.save()
        else:
            print(form.errors)
    return render(request,'admin/product_page.html',{"form":form,'additional_images':additional_images,'id':id,'main_image':product.image,'is_delete':product.is_deleted})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def delete_image(request,id):
    image=AdditionalImage.objects.get(id=id)
    if image:
        os.remove(image.image.path)
        id=image.product.pk
        image.delete()
    return redirect(f'/admin/product/{id}',)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def product_delete(request,id):
    try:
        product=Products.objects.get(id=id)
        product.is_deleted=True
        product.save()
    except:
        
        return redirect('/admin')
    return redirect(f'/admin/product/{id}')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def product_recover(request,id):
    try:
        product=Products.objects.get(id=id)
        product.is_deleted=False
        product.save()
    except:
        return redirect('/admin')
    return redirect(f'/admin/product/{id}')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    form=LoginForm
    if request.POST :
        form=LoginForm(request.POST)
        user=form.is_valid()
        if user:
            login(request,user)
            return redirect('/admin')
            
    return render(request,'admin/login.html',{'form':form})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_logout(request):
    logout(request)
    return redirect('/admin/login')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def users_page(request):
    users=UserModel.objects.all()
    return render(request,'admin/users.html',{'users':users})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def user_view(request,id):
    user=UserModel.objects.get(id=id)
    form=UserEditForm(instance=user)
    print(form)
    if request.POST:
        form=UserEditForm(request.POST ,instance=user)
        if form.is_valid():
            print('valid')
            form.save()
    return render(request,'admin/user_edit.html',{'form':form,'id':id})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def user_change_password(request,id):
    user=UserModel.objects.get(id=id)
    form=SetPasswordForm(user)
    if request.POST:
        form=SetPasswordForm(user,request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin/users')
    return render(request,'admin/user_change_password.html',{'form':form})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def user_block_manage(request,id):
    try:
        user=UserModel.objects.get(id=id)
    except:
        return redirect('')
    
    if user.block==True:
        user.block=False
        user.save()
    else:
        user.block=True
        user.save()
    return redirect('/admin/users')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def categories_list(request):
    categories=Category.objects.all()
    return render(request,'admin/categories.html',{'categories':categories})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def category_page(request,id):
    category=Category.objects.get(id=id)
    form=CategoryAddForm( instance=category)
    if request.POST:
        form=CategoryAddForm(request.POST,instance=category)
        if form.is_valid:
            form.save()

    return render(request,'admin/category_page.html',{'form':form,'id':id,'is_deleted':category.is_deleted})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def category_add(request):
    form=CategoryAddForm
    if request.POST:
        form=CategoryAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/admin/categories')
    return render(request,'admin/category_add.html',{'form':form})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def sub_category_add(request):
    form=SubCategoryAddForm
    if request.POST:
        form=SubCategoryAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/admin/sub-categories')
    return render(request,'admin/category_add.html',{'form':form})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def sub_categories_list(request):
    categories=SubCategory.objects.all()
    return render(request,'admin/sub_categories.html',{'categories':categories})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def sub_category_page(request,id):
    category=SubCategory.objects.get(id=id)
    form=SubCategoryAddForm( instance=category)
    if request.POST:
        form=SubCategoryAddForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
    return render(request,'admin/sub_category_page.html',{'form':form,'id':id,'is_deleted':category.is_deleted})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def category_delete(request,id):
    sub_category=SubCategory.objects.filter(parent_catogery__id=id)
    for category in sub_category:
        category.is_deleted=True
        category.save()
    products=Products.objects.filter(category__id=id)
    for product in products:
        product.is_deleted=True
        product.save()
    category=Category.objects.get(id=id)
    category.is_deleted=True
    category.save()
    return redirect(f'/admin/category/{id}')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def category_recover(request,id):
    sub_category=SubCategory.objects.filter(parent_catogery__id=id)
    for category in sub_category:
        category.is_deleted=False
        category.save()
    products=Products.objects.filter(category__id=id)
    for product in products:
        product.is_deleted=False
        product.save()
    category=Category.objects.get(id=id)
    category.is_deleted=False
    category.save()
    return redirect(f'/admin/category/{id}')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def sub_category_delete(request,id):
    products=Products.objects.filter(sub_category__id=id)
    for product in products:
        product.is_deleted=True
        product.save()
    sub_catogery=SubCategory.objects.get(id=id)
    sub_catogery.is_deleted=True
    sub_catogery.save()
    return redirect(f'/admin/sub-category/{id}')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def sub_category_recover(request,id):
    products=Products.objects.filter(sub_category__id=id)
    for product in products:
        product.is_deleted=False
        product.save()
    sub_catogery=SubCategory.objects.get(id=id)
    sub_catogery.is_deleted=False
    sub_catogery.save()
    return redirect(f'/admin/sub-category/{id}')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def orders(request):
    orders=Orders.objects.all().order_by('-id')
    return render(request,'admin/orders.html',{'orders':orders})
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def order_detials(request,id):
    order=Orders.objects.get(id=id)
    form=OrderForm(instance=order)
    if request.POST:
        form=OrderForm(instance=order,data=request.POST)
        if form.is_valid():
            form.save()
    return render(request,'admin/order_detials.html',{'order':order})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def order_item(request,id):
    order=OrderItem.objects.get(id=id)
    form=OrderForm(instance=order)
    if request.POST:
        form=OrderForm(instance=order,data=request.POST)
        if form.is_valid():
            if 'status' in form.changed_data :
                print(form.cleaned_data.get('status'))
                if form.cleaned_data.get('status') == '-1':
                    user=order.orders.all()[0].user
                    user.wallet+=order.total_price
                    user.save()
            form.save()

    return render(request,'admin/order_item.html',{'form':form})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def coupons(request):
    coupons=Coupons.objects.all()
    return render(request,'admin/coupons.html',{'coupons':coupons})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def add_coupon(request):
    form=CouponsForm
    if request.POST:
        form=CouponsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request,messages.SUCCESS,message='coupon is added')
            return redirect('/admin/coupons')
    return render(request,'admin/add_coupon.html',{'form':form})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/admin/login')
@super_user_check
def coupon_detials(request,id):
    coupon=Coupons.objects.get(id=id)
    form=CouponsForm(instance=coupon)
    if request.POST:
        form=CouponsForm(instance=coupon,data=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request,messages.SUCCESS,message='coupon is saved')
    return render(request,'admin/coupon_detials.html',{'form':form})


