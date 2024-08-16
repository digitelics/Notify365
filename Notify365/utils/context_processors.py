def user_context_processor(request):
  if request.user.is_authenticated:   
    user = request.user
    try:
      avatar = user.avatar.url
    except:
      avatar = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/User-avatar.svg/2048px-User-avatar.svg.png"
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
