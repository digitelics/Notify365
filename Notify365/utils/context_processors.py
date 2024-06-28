def user_context_processor(request):
  if request.user.is_authenticated:   
    user = request.user
    avatar = user.avatar.url
    context = {
        'name':user.name,
        'username':user.user,
        'avatar':avatar,
    }
    return {
        'context_processor': context
    }
  else:
    return {}
