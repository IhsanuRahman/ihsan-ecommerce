from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

handler404 = 'user_app.views.error_404' 
handler500 = 'user_app.views.error_500' 

urlpatterns=[
    path('',views.home,name='home'),
    path('user/profile/',views.user_profile,name='profile'),
    path('user/profile/change-password',views.change_password,name='change-password'),
    path('user/signup/',views.user_signup,name='signup'),
    path('user/login/',views.user_login,name='login'),
    path('user/cart/',views.cart,name='cart'),
    path('user/address/',views.address,name='address'),
    path('user/address/add',views.add_address,name='add_address'),
    path('user/cart/address/add',views.add_address_checkout,name='add_address_checkout'),
    path('user/address/<id>/edit',views.edit_address,name='edit_address'),
    path('user/cart/<id>/delete',views.remove_from_cart),
    path('user/cart/<id>/edit',views.edit_cart),
    path('user/logout/',views.user_logout,name='logout'),
    path("user/product/<id>",views.product_detials_page,name='product_detials'),
    path('user/products',views.products),
    path("user/category/<id>",views.category,name='category'),
    path("user/sub-category/<id>",views.sub_category,name='sub_category'),
    path("user/product/<id>/add_to_cart",views.add_to_cart,name='add_to_cart'),
    path('user/verification',views.otp_verification,name='otp_verification'),
    path('user/reset-otp',views.reset_otp,name='reset_otp'),
    path('user/forgot-password',views.forgot_password,name='forgot-password'),
    path('user/forgot-password/verification',views.verify_forgot_pass),
    path('user/forgot-password/change',views.user_reset_pass),
    path('search/',views.search_group),
    path('search-result/<search>',views.search_result_page),
    path('search-result/',views.search_result_page),
    path('user/orders/',views.orders,name='orders'),
    path('user/orders/payment',views.checkout_payment),
    path('user/order/<id>/invoice',views.invoice),
    path('user/order/<id>/cancel',views.cancel_order,name='cancel_order'),
    path('user/order/<id>/', views.order_details),
    path('user/wishlist/add',views.add_to_wishlist),
    path('user/wishlist/<id>/remove',views.remove_from_wishlists),
    path('user/wishlists',views.wish_lists),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)