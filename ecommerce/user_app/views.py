import datetime
from django.http import  HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from admin_app.models import Sales
from .forms import AddressForm, BrandFilter, CancelForm, FilterForm, ForgotPasswordForm, LoginForm, PasswordResetForm,RegisterForm,OTPForm, SortForm, UserEditForm,PasswordEditForm as PasswordChangeForm
from django.contrib.auth import login,logout
from .models import  Address, Cart, Coupons, OrderItem, Orders, WishList,status_choise, Products, SubCategory,UserModel, UserModelOperation,Category, UserTemp
from .utils import otp_verify,otp_generator
from django.views.decorators.cache import cache_control
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib import messages
import razorpay
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required


def home(request):
    products=Products.public.filter(category__name="Shoes")
    tshirts=Products.public.filter(sub_category__name="Jeans")
    categories=Category.public.all().filter(products__is_deleted=False).distinct()
    sub_categories=SubCategory.public.all()
    banner_products=[]
    for category in categories:
        product=Products.public.filter(category=category).first()
        if product:
            banner_products.append([product,category]) 
    return render(request,'user/index.html',{'products':products,'tshirts':tshirts,'banner_products':banner_products,'categories':categories,'sub_categories':sub_categories})


def error_404(request, exception):
    return render(request, 'myapp/error_404.html', status=404)
 


def error_500(request):
    return render(request, 'myapp/error_505.html', status=500)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_signup(request):
    
    form=RegisterForm()
    if request.POST:
        form=RegisterForm(request.POST)
        if form.is_valid():
            user=form.save()

            if user:
                request.session['user_id']=user.id
                user=UserTemp.objects.filter(id=user.id).first()
                otp_generator(request,user)
                return redirect('otp_verification')
    return render(request,'user/signup.html',{'form':form})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def otp_verification(request):
    if request.user.is_authenticated:
        return redirect('home')
    form=OTPForm
    
    if datetime.datetime.now()-datetime.datetime.strptime(request.session['otp_datetime'],'%Y-%m-%d %H:%M:%S.%f')>datetime.timedelta(minutes=3):
        
        del request.session['otp']
        del request.session['user_id']
        del request.session['otp_datetime']
        return redirect('signup')
    if request.POST:
        form=OTPForm(request.POST)
        if form.is_valid():
            if otp_verify(request,form.cleaned_data.get('otp')):
                opertion_id=request.session['user_id']
                print(opertion_id)
                if opertion_id:
                    op=UserModelOperation.objects.get(user_model=opertion_id)
                    if op.operation=='create':
                        user=op.user_model
                        create_user=UserModel.objects.create(username=user.username,first_name=user.first_name,last_name=user.last_name,email=user.email,password=user.password)
                        create_user.save()
                        user.delete()
                        del request.session['otp']
                        del request.session['user_id']
                        del request.session['otp_datetime']
                return redirect('login')
            else :
                form.add_error('otp','wrong otp')
    timeout=(datetime.datetime.now()-datetime.timedelta(minutes=2) -datetime.datetime.strptime(request.session['otp_datetime'],'%Y-%m-%d %H:%M:%S.%f')).total_seconds()
    return render(request,'user/otp_verification.html',{'form':form,'timeout':abs(int(timeout))})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def reset_otp(request):
    if request.user.is_authenticated or not request.session['otp_datetime'] or not request.session['otp']:
        return redirect('home')
    if datetime.datetime.now()-datetime.datetime.strptime(request.session['otp_datetime'],'%Y-%m-%d %H:%M:%S.%f')>datetime.timedelta(minutes=2):
        
        id=request.session['user_id']
        user=UserTemp.objects.filter(id=id).first()
        if not user:
            print('um')
            user=UserModel.objects.filter(id=id).first()
        
        otp_generator(request,user)
    if datetime.datetime.now()-datetime.datetime.strptime(request.session['otp_datetime'],'%Y-%m-%d %H:%M:%S.%f')>datetime.timedelta(minutes=3):
        del request.session['otp']
        del request.session['user_id']
        del request.session['otp_datetime']
        return redirect('signup')
    return redirect('otp_verification')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def forgot_password(request):
    form=ForgotPasswordForm
    if request.POST:
        form=ForgotPasswordForm(request.POST)
        if form.is_valid():
            email=form.cleaned_data.get('email')
            user=UserModel.objects.get(email=email)
            request.session['user_id']=user.id
            otp_generator(request,user,email)
            return redirect('/user/forgot-password/verification')
    return render(request,'user/forgot_password.html',{'form':form})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def verify_forgot_pass(request):
    form=OTPForm
    if datetime.datetime.now()-datetime.datetime.strptime(request.session['otp_datetime'],'%Y-%m-%d %H:%M:%S.%f')>datetime.timedelta(minutes=3):
        
        del request.session['otp']
        del request.session['user_id']
        del request.session['otp_datetime']
        return redirect('signup')
    if request.POST:
        form=OTPForm(request.POST)
        if form.is_valid():
            if otp_verify(request,form.cleaned_data.get('otp')):
                del request.session['otp']
                del request.session['otp_datetime']
                return redirect('/user/forgot-password/change')
    timeout=(datetime.datetime.now()-datetime.timedelta(minutes=2) -datetime.datetime.strptime(request.session['otp_datetime'],'%Y-%m-%d %H:%M:%S.%f')).total_seconds()
    return render(request,'user/otp_verification.html',{'form':form,'timeout':abs(int(timeout))})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_reset_pass(request):
    id=request.session['user_id']
    user= UserModel.objects.get(id=id)
    form=PasswordResetForm(user=user)
    if request.POST:
        form=PasswordResetForm(user,request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request,messages.INFO,'password is changed')
            del request.session['user_id']
            return redirect('/user/login')
    
    return render(request,'user/password_change.html',{'form':form})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_login(request):    
    if request.user.is_authenticated :
        return redirect('home')
    form=LoginForm()
    if request.POST:
        form=LoginForm(request.POST)
        user=form.is_valid()
        if user:
            login(request,user)
            messages.add_message(request,messages.SUCCESS,'login success')
            return redirect('home')
    return render(request,'user/login.html',{'form':form})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def user_logout(request):
    if request.user.is_authenticated and request.META.get('HTTP_REFERER') is not None:
       logout(request)
    return redirect('home')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def user_profile(request):
    user=UserModel.objects.get(id=request.user.id)
    form=UserEditForm(instance=user)
    if request.POST:
        form=UserEditForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
            messages.add_message(request,messages.INFO,'saved')
    
    return render(request,'user/profile.html',{'form':form})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def change_password(request):
    user=User.objects.get(id=request.user.pk)
    form=PasswordChangeForm(user=user)
    if request.POST:
        form=PasswordChangeForm(user=user,data=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request,messages.INFO,'password is changed login again')
            return redirect('/user/login')
    return render(request,'user/change_password.html',{'form':form})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def address(request):
    address=Address.objects.filter(user__id=request.user.id)
    return render(request,'user/address.html',{'address':address})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def add_address(request):
    form=AddressForm
    if request.POST:
        form=AddressForm(request.POST)
        if form.is_valid():
            address=form.save(commit=False)
            address.user=UserModel.objects.get(id=request.user.id)
            
            if Address.objects.filter(user=address.user,holder_name=address.holder_name,phone_number=address.phone_number,country=address.country,address=address.address,pin_code=address.pin_code,town_or_city=address.town_or_city,state=address.state,district=address.district).exists():
                form.add_error('__all__','already exists')

            else:
                address.save()
                messages.add_message(request,messages.INFO,'new address is created')
                return redirect(request.META.get('HTTP_REFERER'))
    return render(request,'user/add_address.html',{'form':form})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def edit_address(request,id):
    try:
        address= Address.objects.get(id=id)
    except:
        return redirect('user/address')
    form=AddressForm(instance=address)
    if request.POST:
        form=AddressForm(request.POST,instance=address)
        if form.is_valid():
            address=form.save(commit=False)
            
            if Address.objects.filter(user=address.user,holder_name=address.holder_name,phone_number=address.phone_number,country=address.country,address=address.address,pin_code=address.pin_code,town_or_city=address.town_or_city,state=address.state,district=address.district).exclude(id=id).exists():
                form.add_error('__all__','already exists')

            else:
                address.save()
                messages.add_message(request,messages.INFO,'saved')
                return redirect('/user/address')
    return render(request,'user/edit_address.html',{'form':form})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def add_address_checkout(request):
    form=AddressForm
    if request.POST:
        form=AddressForm(request.POST)
        if form.is_valid():
            address=form.save(commit=False)
            address.user=UserModel.objects.get(id=request.user.id)
            if Address.objects.filter(user=address.user,holder_name=address.holder_name,phone_number=address.phone_number,country=address.country,address=address.address,pin_code=address.pin_code,town_or_city=address.town_or_city,state=address.state,district=address.district).exists():
                form.add_error('__all__','already exists')
            else:
                address.save()
                messages.add_message(request,messages.INFO,'new address is created')
                return redirect('/user/cart')
    return render(request,'user/add_address.html',{'form':form})


def product_detials_page(request,id):
    try:
        product=Products.public.get(id=id)
    except:
        return redirect('home')
    options=product.options.all()
    additional_info=product.additional_info.all()
    additional_image=product.additional_images.all()
    similar_products=Products.public.filter((Q(sub_category=product.sub_category)|Q(category=product.category))).distinct()
    return render(request,'user/product_detials.html',{'product':product,'options':options,'additional_info':additional_info,'additional_image':additional_image,'similar_products':similar_products})


def search_group(request):
    search = request.GET.get('search')
    payload = []
    if search:
        results = Products.public.filter(title__icontains=search)
        for result in results:
            payload.append({
                'textin': result.title,
                'id': result.pk,
                'type':"product"
            })
        results = SubCategory.public.filter(name__icontains=search)
        for result in results:
            payload.append({
                'textin': result.name,
                'id': result.pk,
                'type':"subcategory"
            })
        results = Category.public.filter(name__icontains=search)
        for result in results:
            payload.append({
                'textin': result.name,
                'id': result.pk,
                'type':"category"
            })
    return JsonResponse({
        'status': True,
        'payload': payload
    })



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def add_to_cart(request,id):
    if request.user.is_authenticated:
        if request.POST:
            if Cart.objects.filter(product=Products.public.get(id=id),user=UserModel.objects.filter(id=request.user.pk).first(),option=request.POST.get('option')):
                messages.add_message(request,messages.WARNING,'product is already exists')
                return redirect(request.META.get('HTTP_REFERER'),id=id)
            Cart.objects.create(product=Products.public.get(id=id),user=UserModel.objects.filter(id=request.user.pk).first(),quantity=request.POST.get('quantity'),option=request.POST.get('option'))
            messages.add_message(request,messages.INFO,mark_safe('item added to <a class="m-0 p-0 " href="/user/cart">cart</a>'))
        return redirect(request.META.get('HTTP_REFERER'),id=id)
    else : return redirect('login')



from django.conf import settings
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def cart(request):
    products=Cart.objects.filter(user=request.user)
    address=Address.objects.filter(user=request.user)
    total_price=0.0
    for item in products:
        total_price+=float(item.product.get_offered_price())*int(item.quantity)
    coupon=None
    payment=None
    if request.POST:
        print(request.POST.get('coupon',False))
        if request.POST.get('address') and request.POST.get('shipping'):
            if request.POST.get('coupon',False):
                        code=request.POST.get('coupon')
                        coupon=Coupons.objects.filter(code=code)
                        if coupon is not None:
                            if coupon[0].valid_till:
                                if datetime.datetime.now()<coupon[0].valid_till.replace(tzinfo=None) and not coupon[0].is_expired:
                                    if UserModel.objects.get(id=request.user.pk) not in coupon[0].applied_users.all():
                                        if coupon[0].minimum_purchase<=total_price:
                                            total_price-=(coupon[0].offer*total_price)/100
                                            total_price=round(total_price,2)
                                            
                                            
                                        else:
                                            messages.add_message(request,messages.WARNING,f'coupon want minimum {coupon[0].minimum_purchase} purchase')
                                            return render(request,'user/cart.html',{'products':products,'total_price':round(total_price,2),'address':address,})
                                    else:
                                        messages.add_message(request,messages.WARNING,'coupon already applied')
                                        return render(request,'user/cart.html',{'products':products,'total_price':round(total_price,2),'address':address,})
                                else:
                                    messages.add_message(request,messages.WARNING,'coupon expired')
                                    return render(request,'user/cart.html',{'products':products,'total_price':round(total_price,2),'address':address,})
                            elif not coupon[0].is_expired:
                                    if UserModel.objects.get(id=request.user.pk) not in coupon[0].applied_users.all():
                                        if coupon[0].minimum_purchase<=total_price:
                                            total_price-=(coupon[0].offer*total_price)/100
                                            total_price=round(total_price,2)
                                        else:
                                            messages.add_message(request,messages.WARNING,f'coupon want minimum {coupon[0].minimum_purchase} purchase')
                                            return render(request,'user/cart.html',{'products':products,'total_price':round(total_price,2),'address':address,})
                                    else:
                                        messages.add_message(request,messages.WARNING,'coupon already applied')
                                        return render(request,'user/cart.html',{'products':products,'total_price':round(total_price,2),'address':address,})
                        else:
                            messages.add_message(request,messages.WARNING,'coupon not exist')
                            return render(request,'user/cart.html',{'products':products,'total_price':round(total_price,2),'address':address,})
            orders=Orders(user=UserModel.objects.get(id=request.user.pk),address=address.get(id=int(request.POST.get('address'))),payment_method=request.POST.get('shipping'),is_conformed=False,total_price=round(total_price,2))
            if coupon:
                orders.coupon=coupon[0]
            orders.save()
            for product in products:
                print(product.product.get_offered_price()*product.quantity,'price')
                product_total_price=(product.product.get_offered_price()*product.quantity)
                orderItem=OrderItem(product=product.product,
                    quantity=product.quantity,
                    total_price=product_total_price,
                    option=product.option,
                    status=0
                )
                orderItem.save()
                print(orderItem.total_price,'product to price',product_total_price)
                orders.order_items.add(orderItem)
                print(request.POST.get('shipping'))
            if request.POST.get('shipping')=='cash-on-delivery':
                orders.is_conformed=True
                orders.save()
                products.delete()
                if coupon:
                    coupon[0].applied_users.add(UserModel.objects.get(id=request.user.pk))
                sales=Sales.objects.filter(date=orders.ordered_datetime.date()).first()
                if sales:
                    sales.orders.add(orders)
                    sales.total_money=round(sales.total_money+orders.total_price,2)
                else:
                    sales=Sales.objects.create(date=orders.ordered_datetime.date(),total_money=round(orders.total_price,2))
                    sales.orders.add(orders)
                sales.save()
                return render(request,'user/order_success.html')
            elif request.POST.get('shipping')=='pay-online':
                print('payonline')
                for p in products:
                    orders.carts.add(p)
                orders.is_conformed=False
                orders.save()
                if coupon:
                    coupon[0].applied_users.add(UserModel.objects.get(id=request.user.pk))
                client=razorpay.Client(auth=(settings.RAZORPAY_KEY,settings.RAZORPAY_SECRET))
                payment=client.order.create({'amount':int(round(total_price,2)*100),'currency':'INR','payment_capture':1}) 
                orders.razorpay_order_id=payment.get('id')
                orders.save()
                return render(request,'user/cart.html',{'products':products,'total_price':round(total_price,2),'address':address,'payment':payment,'pay':True,'razorpay_key':settings.RAZORPAY_KEY})
            elif request.POST.get('shipping')=='wallet':
                user=UserModel.objects.get(id=request.user.pk)
                if user.wallet>=orders.total_price:
                    user.wallet-=orders.total_price
                    user.wallet=round(user.wallet,2)
                    orders.is_conformed=True
                    orders.save()
                    products.delete()
                    user.save()
                    if coupon:
                        coupon[0].applied_users.add(UserModel.objects.get(id=request.user.pk))
                    return render(request,'user/order_success.html')
                else:messages.add_message(request,messages.WARNING,message='not enogh money in wallet')
    return render(request,'user/cart.html',{'products':products,'total_price':round(total_price,2),'address':address,'payment':payment,'pay':False})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def checkout_payment(request):
    if request.POST:
        order_id=request.POST.get('razorpay_order_id')
        payment_id=request.POST.get('razorpay_payment_id')
        signature=request.POST.get('razorpay_signature')
        print(order_id)
        order=Orders.objects.get(razorpay_order_id=order_id)
        order.is_conformed=True
        order.razorpay_payment_id=payment_id
        order.razorpay_signature=signature
        order.payment_method
        order.save()
        order.carts.all().delete()
        sales=Sales.objects.filter(date=order.ordered_datetime.date()).first()
        if sales:
            sales.orders.add(order)
            sales.total_money=round(sales.total_money+order.total_price,2)
        else:
            sales=Sales.objects.create(date=order.ordered_datetime.date(),total_money=round(order.total_price,2))
            sales.orders.add(order)
        sales.save()
        return render(request,'user/order_success.html')


from xhtml2pdf import pisa
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def invoice(request,id):
    order=Orders.objects.get(id=id,user__id=request.user.id)
    template_path = 'user/invoice.html'
    context = {'orders':order}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
    


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def remove_from_cart(request,id):
    try:
        cart=Cart.objects.get(id=id)
    except:
        return redirect('/user/cart/')
    cart.delete()
    messages.add_message(request,messages.WARNING,'item removed form cart')
    return redirect('/user/cart/')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def edit_cart(request,id):
    if request.POST:
        try:
            cart=Cart.objects.get(id=id)
        except:
            return redirect('/user/cart/')
        quantity=int(request.POST['quantity'])
        product=Products.objects.get(id=cart.product.pk)
        if quantity<=10 and quantity>0 and quantity<=product.quantity:
            cart.quantity=quantity
            cart.save()
        elif quantity>10:
            messages.add_message(request,messages.WARNING,"only maximum 10 quantity will allow to order.")
        
    return redirect('/user/cart/')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def orders(request):
    orders=Orders.objects.filter(user__id=request.user.id,is_conformed=True).order_by('-id')
    return render(request,'user/orders.html',{'orders':orders,'status_choise':status_choise,})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def order_details(request,id):
    orderItem=OrderItem.objects.get(id=id)
    order=orderItem.orders.all()[0]
    return render(request,'user/order_details.html',{'order':order,'orderItem':orderItem,'status_choise':status_choise,})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def cancel_order(request,id):
    order=OrderItem.objects.get(id=id)
    form=CancelForm
    if request.POST:
        form=CancelForm(request.POST)
        if form.is_valid():
            if order:
                model=form.save(commit=False)
                order.status=status_choise[0][0]
                order.save()
                model.order=order
                model.save()
                if order.orders.all()[0].payment_method == 'pay-online' or order.orders.all()[0].payment_method == 'wallet' :
                    user=UserModel.objects.get(id=request.user.pk)
                    user.wallet+=order.total_price
                    user.wallet=round(user.wallet,2)
                    user.save()
                    messages.add_message(request,messages.INFO,message='order is cancelled and your refund will added in wallet')
                return redirect('/user/orders')
    return render(request,'user/order_cancel.html',{'form':form})


def search_result_page(request,search=None):
    if search==None or request.GET.get('search'):
        print(request.GET)
        search=request.GET.get('search')
        print(search,'jfs')
    categories=Category.public.all()
    category_filter=FilterForm(categories,)
    sub_categories=SubCategory.objects.all()
    sub_catogery_form=FilterForm(categories=sub_categories)
    print(request.POST)
    products=Products.public.filter(Q(title__icontains=search)|Q(category__name__icontains=search)|Q(sub_category__name__icontains=search)).distinct()
    sortform=SortForm
    brand_filter=BrandFilter(products)
    page_number=1
    if request.POST:
        category_filter=FilterForm(categories,request.POST,)
        category_list=[]
        brand_list=[]
        sub_catogery_list=[]
        if category_filter.is_valid():
            for k,v in category_filter.cleaned_data.items():
                print(v)
                if v:
                    category_list.append(k)
        if category_list:
            products=products.filter(category__name__in=category_list)
        brand_filter=BrandFilter(products,request.POST)
        sub_categories=SubCategory.objects.filter(id__in=products.values_list('sub_category',flat=True).distinct())
        sub_catogery_form=FilterForm(sub_categories,request.POST)
        if sub_catogery_form.is_valid():
            for k,v in sub_catogery_form.cleaned_data.items():
                print(v)
                if v:
                    sub_catogery_list.append(k)
        if sub_catogery_list:
            products=products.filter(sub_category__name__in=sub_catogery_list)
        if brand_filter.is_valid():
            for k,v in brand_filter.cleaned_data.items():
                if v:
                    brand_list.append(k)
        brand_filter=BrandFilter(products,request.POST)
        print(brand_list)
        if brand_list:
            products=products.filter(brand__in=brand_list)
        if request.POST.get('sortby'):
            sortform=SortForm(request.POST)
            if request.POST.get('sortby') =='-price':
                products=products.order_by('-price')
            elif request.POST.get('sortby') == 'price':
                products=products.order_by('price')
        if request.POST.get("page"):
            
            page_number = request.POST.get("page")
    categories_checkbox={}
    if request.POST:
        for k,v in request.POST.items():
            categories_checkbox[k]=v
    paginator = Paginator(products, 15)
    try:
        page_obj = paginator.get_page(page_number)
    except:
        page_obj = paginator.get_page(1)
    return render(request,'user/search-result.html',{'products':page_obj,'categories':categories,'sortform':sortform,'category_filter':category_filter,'brand_filter':brand_filter,'total_pages':range(1,paginator.num_pages+1),'page_number':int(page_number),'sub_catogery_form':sub_catogery_form})


def products(request):
    categories=Category.public.all()
    category_filter=FilterForm(categories,)
    sub_categories=SubCategory.objects.all()
    sub_catogery_form=FilterForm(categories=sub_categories)
    print(request.POST)
    products=Products.public.all()
    sortform=SortForm
    brand_filter=BrandFilter(products)
    page_number=1
    if request.POST:
        category_filter=FilterForm(categories,request.POST,)
        category_list=[]
        brand_list=[]
        sub_catogery_list=[]
        if category_filter.is_valid():
            for k,v in category_filter.cleaned_data.items():
                print(v)
                if v:
                    category_list.append(k)
        if category_list:
            products=products.filter(category__name__in=category_list)
        brand_filter=BrandFilter(products,request.POST)
        sub_categories=SubCategory.objects.filter(id__in=products.values_list('sub_category',flat=True).distinct())
        sub_catogery_form=FilterForm(sub_categories,request.POST)
        if sub_catogery_form.is_valid():
            for k,v in sub_catogery_form.cleaned_data.items():
                print(v)
                if v:
                    sub_catogery_list.append(k)
        if sub_catogery_list:
            products=products.filter(sub_category__name__in=sub_catogery_list)
        if brand_filter.is_valid():
            for k,v in brand_filter.cleaned_data.items():
                if v:
                    brand_list.append(k)
        brand_filter=BrandFilter(products,request.POST)
        print(brand_list)
        if brand_list:
            products=products.filter(brand__in=brand_list)
        if request.POST.get('sortby'):
            sortform=SortForm(request.POST)
            if request.POST.get('sortby') =='-price':
                products=products.order_by('-price')
            elif request.POST.get('sortby') == 'price':
                products=products.order_by('price')
        if request.POST.get("page"):
            
            page_number = request.POST.get("page")
    categories_checkbox={}
    if request.POST:
        for k,v in request.POST.items():
            categories_checkbox[k]=v
    paginator = Paginator(products, 15)
    try:
        page_obj = paginator.get_page(page_number)
    except:
        page_obj = paginator.get_page(1)
    return render(request,'user/search-result.html',{'products':page_obj,'categories':categories,'sortform':sortform,'category_filter':category_filter,'brand_filter':brand_filter,'total_pages':range(1,paginator.num_pages+1),'page_number':int(page_number),'sub_catogery_form':sub_catogery_form})


def category(request,id):
    products=Products.public.filter(category__id=id).distinct()
    print(products[0].sub_category,'hel')
    page_number=1
    sortform=SortForm
    brand_filter=BrandFilter(products)
    sub_categories=SubCategory.objects.filter(parent_catogery_id=id)
    sub_catogery_form=FilterForm(categories=sub_categories)
    sub_catogery_list=[]
    brand_list=[]
    if request.POST.get('sortby'):
        sortform=SortForm(request.POST)
        sub_catogery_form=FilterForm(sub_categories,request.POST)
        
        if request.POST.get('sortby') =='-price':
            products=products.order_by('-price')
        elif request.POST.get('sortby') == 'price':
            products=products.order_by('price')
        if sub_catogery_form.is_valid():
            for k,v in sub_catogery_form.cleaned_data.items():
                print(v)
                if v:
                    sub_catogery_list.append(k)
        if sub_catogery_list:
            products=products.filter(sub_category__name__in=sub_catogery_list)
        brand_filter=BrandFilter(products,request.POST)
        if brand_filter.is_valid():
            for k,v in brand_filter.cleaned_data.items():
                if v:
                    brand_list.append(k)
        if request.POST.get("page"):
            page_number = request.POST.get("page")
    
    if brand_list:
            products=products.filter(brand__in=brand_list)
    paginator = Paginator(products, 15)
    try:
        page_obj = paginator.get_page(page_number)
    except:
        page_obj = paginator.get_page(1)
    return render(request,'user/category-list.html',{'products':page_obj,'sortform':sortform,'category_filter':sub_catogery_form,'total_pages':range(1,paginator.num_pages+1),'page_number':int(page_number),'brand_filter':brand_filter})


def sub_category(request,id):
    products=Products.public.filter(sub_category__id=id).distinct()
    
    page_number=1
    sortform=SortForm
    brand_filter=BrandFilter(products)
    brand_list=[]
    if request.POST:
        if request.POST.get('sortby'):
            sortform=SortForm(request.POST)
            if request.POST.get('sortby') =='-price':
                products=products.order_by('-price')
            elif request.POST.get('sortby') == 'price':
                products=products.order_by('price')
        brand_filter=BrandFilter(products,request.POST)
        if brand_filter.is_valid():
            for k,v in brand_filter.cleaned_data.items():
                if v:
                    brand_list.append(k)
        if request.POST.get("page"):
            page_number = request.POST.get("page")
    if brand_list:
            products=products.filter(brand__in=brand_list)
    paginator = Paginator(products, 15)
    try:
        page_obj = paginator.get_page(page_number)
    except:
        page_obj = paginator.get_page(1)
    return render(request,'user/subcategory-list.html',{'products':page_obj,'sortform':sortform,'total_pages':range(1,paginator.num_pages+1),'page_number':int(page_number),'brand_filter':brand_filter})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def add_to_wishlist(request):
    if request.user.is_authenticated:
        if request.POST:
            id=request.POST.get('id')
            product=Products.objects.get(id=id)
            wishList=WishList.objects.get_or_create(user=UserModel.objects.get(id=request.user.pk))[0]
            if product not in  wishList.products.all():
                wishList.products.add(product)
                wishList.save()
                messages.add_message(request,messages.INFO,mark_safe('added to <a class="m-0 p-0 " href="/user/wishlists">wishlist</a>'))
            else:messages.add_message(request,messages.WARNING,'already exist in whish list')
        return redirect('product_detials',id=id)
    else : return redirect('login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def wish_lists(request):
    
    return render(request,'user/wishlist.html',{'products':WishList.objects.get(user=UserModel.objects.get(id=request.user.pk)).products.all()})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/user/login')
def remove_from_wishlists(request,id):
    
    product=Products.objects.get(id=id)
    wishlist=WishList.objects.get(user=UserModel.objects.get(id=request.user.pk))
    wishlist.products.remove(product)
    wishlist.save()
    return redirect('/user/wishlists')