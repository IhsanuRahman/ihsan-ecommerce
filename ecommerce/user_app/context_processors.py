from .models import UserModel

def user_model(request):
    try:
        return {'user_model':UserModel.objects.filter(block=False).get(id=request.user.pk)}
    except:
        return {}