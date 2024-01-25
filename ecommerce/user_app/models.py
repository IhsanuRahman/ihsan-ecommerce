from django.db import models
from django.contrib.auth.models import User,AbstractUser
from django.core.validators import MinLengthValidator,MinValueValidator,MaxValueValidator,RegexValidator
class NonDelete(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class UserModel(User):
    block=models.BooleanField(default=False)
    wallet=models.FloatField(default=0.0)


class UserTemp(models.Model):
    username=models.CharField(max_length=50)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    email=models.EmailField(max_length=50)
    password=models.CharField(max_length=50)
    stored_time=models.DateTimeField(auto_now=True)    

operation_choise=[('create','create'),('edit','edit')]
class UserModelOperation(models.Model):
    operation=models.CharField(choices=operation_choise,default='create',max_length=6)
    user_model=models.OneToOneField(UserTemp,on_delete=models.CASCADE)
    
class Category(models.Model):
    def __str__(self) -> str:
        return self.name
    name=models.CharField(max_length=50,unique=True)
    offer=models.FloatField(validators=[MinValueValidator(0.0),MaxValueValidator(99.9)],default=0)
    is_deleted=models.BooleanField(default=False)
    objects=models.Manager() 
    public=NonDelete()

class SubCategory(models.Model):
    parent_catogery=models.ForeignKey(Category,on_delete=models.CASCADE,related_name='sub_category') 
    name=models.CharField(max_length=50,unique=True)
    is_deleted=models.BooleanField(default=False)
    def __str__(self) -> str:
        return self.name
    objects=models.Manager() 
    public=NonDelete()

class Products(models.Model):
    title=models.CharField(max_length=50,unique=True)
    image=models.ImageField(upload_to ='uploads/title-images',)
    brand=models.CharField(max_length=50)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,null=False,related_name='products')
    sub_category=models.ForeignKey(SubCategory,on_delete=models.CASCADE,null=False, related_name='products')
    price=models.FloatField(max_length=50)
    offer=models.FloatField(validators=[MinValueValidator(0.0),MaxValueValidator(99.9)],default=0)
    quantity=models.IntegerField()
    gender=models.CharField(max_length=50)
    description=models.TextField(max_length=300)
    is_deleted=models.BooleanField(default=False)
    objects=models.Manager() 
    public=NonDelete()
    def get_offered_price(self):
        price=self.price
        offer=self.offer+self.category.offer
        if offer == 0 :
            return price
        return round(price-(price*offer/100), 2)

    def __str__(self) -> str:
        return self.title

class AdditionalImage(models.Model):
    image=models.ImageField(upload_to ='uploads/additional-images')
    product=models.ForeignKey(Products,on_delete=models.CASCADE,null=False, related_name='additional_images')

class AdditionalInfo(models.Model):
    product=models.ForeignKey(Products,on_delete=models.CASCADE, related_name='additional_info')
    attribute=models.CharField(max_length=50)
    value=models.CharField(max_length=50)



class ProductOptions(models.Model):
    product=models.ManyToManyField(Products,related_name="options")
    name=models.CharField(max_length=50)



class Cart(models.Model):
    product=models.ForeignKey(Products,on_delete=models.DO_NOTHING)
    user=models.ForeignKey(UserModel,on_delete=models.CASCADE)
    option=models.CharField(max_length=50)
    quantity=models.IntegerField()
    datetime=models.DateTimeField(auto_now=True)



class Address(models.Model):
    user=models.ForeignKey(UserModel,on_delete=models.CASCADE,null=False)
    holder_name=models.CharField(max_length=20, validators=[MinLengthValidator(4)],null=False)
    phone_number=models.BigIntegerField(null=False)
    country=models.CharField(max_length=25,null=False)
    address=models.TextField(null=False)
    town_or_city=models.CharField(max_length=25,null=False)
    state=models.CharField(max_length=25,null=False)
    district=models.CharField(max_length=25,null=False)
    pin_code=models.IntegerField(null=False)
    class Meta:
         unique_together = ['user','holder_name','phone_number','country','address','pin_code','town_or_city','state','district']
    def __str__(self) -> str:
        return self.address
status_choise=(
        ('-1','cancelled'),
        ('0','ordered'),
        ('1','packed'),
        ('2','shipped'),
        ('3','out for delivery'),
        ('4','delivered'),

    )
class OrderItem(models.Model):
    total_price=models.FloatField()
    product=models.ForeignKey(Products,on_delete=models.DO_NOTHING)
    quantity=models.IntegerField()
    option=models.CharField(max_length=50)
    status=models.CharField(max_length=50,choices=status_choise)
    receive_datetime=models.DateTimeField(null=True)

    
class Coupons(models.Model):
    code=models.CharField(max_length=50,unique=True,validators=[MinLengthValidator(5),RegexValidator(regex=' +',inverse_match=True,message='space is not allowed')])
    valid_till=models.DateTimeField(null=True)
    offer=models.FloatField(validators=[MinValueValidator(0.0),MaxValueValidator(99.9)],default=0.0)
    applied_users=models.ManyToManyField(UserModel)
    minimum_purchase=models.IntegerField(null=True,default=0)
    is_expired=models.BooleanField(default=False,null=True)

payment_choises=[
    ('cash-on-delivery','Cash on delivery'),
    ('pay-online','Pay Online'),
    ('wallet','Wallet'),
]
class Orders(models.Model):
    order_items=models.ManyToManyField(OrderItem,related_name='orders')
    user=models.ForeignKey(UserModel,on_delete=models.DO_NOTHING)
    total_price=models.FloatField()
    ordered_datetime=models.DateTimeField(auto_now=True)
    payment_method=models.CharField(max_length=16,choices=payment_choises)
    address=models.ForeignKey(Address,on_delete=models.DO_NOTHING,null=False)
    coupon=models.ForeignKey(Coupons,null=True,on_delete=models.SET_NULL)
    is_conformed=models.BooleanField(default=False)
    razorpay_payment_id=models.CharField(max_length=56,null=True,default=None)
    razorpay_order_id=models.CharField(max_length=56,null=True,default=None)
    razorpay_signature=models.CharField(max_length=56,null=True)
    carts=models.ManyToManyField(Cart,related_name='orders')


class OrderCancellDetials(models.Model):
    cancelled_on=models.DateTimeField(auto_now=True)
    order=models.ForeignKey(OrderItem,on_delete=models.DO_NOTHING,null=False)
    reason=models.TextField(null=False,validators=[MinLengthValidator(10)])


class WishList(models.Model):
    user=models.OneToOneField(UserModel,on_delete=models.DO_NOTHING)
    products=models.ManyToManyField(Products,related_name='wish_list')
    