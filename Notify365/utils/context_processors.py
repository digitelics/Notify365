def user_context_processor(request):
  if request.user.is_authenticated:   
    user = request.user
    try:
      avatar = user.avatar.url
    except:
      avatar = "https://notify365.us/static/images/customer-avatar.png"
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
