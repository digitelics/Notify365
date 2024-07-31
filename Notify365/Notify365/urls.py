
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('client/', views.client_view.client, name="client"),
    path('', views.index, name="dashboard"),
    path('test/', views.test, name='test'),
    path('login/', views.login_view.login, name="login"),
    path('registration/', views.registration_view.registration, name="registration"),
    path('setting/', views.setting_view.setting, name="setting"),
    path('setting/account/', views.account_view.account, name="account"),
    path('setting/account/edit', views.account_view.edit_account, name="edit-account"),
    path('setting/company/', views.company_view.company, name="company"),
    path('setting/security/', views.security_view.security, name="security"),
    path('setting/notification/', views.notification_view.notification, name="notification"),

    path('customers/', views.customer_view.customer, name='customers'),
    path('customers/add', views.customer_view.add_customer_view, name='add-customer'),
    path('customers/<int:customer_id>/', views.customer_view.customer_detail_view, name='customer_detail'),
    #path('customers/edit/<int:id>', views.customer_view.customer, name='customer'),
    #path('customers/delete/<int:id>', views.customer_view.customer, name='customer'),

    path('customers/deal/add', views.customer_service_view.add_deal_view, name='add-deal'),
    path('customers/note/add', views.note_view.add_note_view, name='add-note'),
    path('customers/contact/add', views.contact_view.add_contact_view, name='add-contact'),
    path('customers/document/update', views.document_view.update_document_view, name='update-document'),
    path('customers/send/text/', views.customer_send_text_message_view.customer_send_message, name='customer-send-text'),
    path('sms/send/chat/', views.notify_view.send_message_chat, name='send-chat'),

    path('notify/', views.notify_view.notify, name="notify"),
    path('calendar/', views.calendar_views.calendar, name='calendar'),
    path('calendar/today', views.calendar_views.day_calendar, name='day'),
    path('setting/general_settings/<str:tab>', views.general_view.GeneralSettingView.as_view(), name='general_setting'),
    path('setting/general_settings/templateCategory/add', views.general_view.add_template_category, name='template-category-add'),
    path('setting/general_settings/templateCategory/edit/<int:id>', views.general_view.edit_template_category, name='template-category-edit'),
    path('setting/general_settings/templateCategory/remove/<int:id>', views.general_view.delete_template_category, name='template-category-remove'),
    path('setting/general_settings/providerType/add', views.general_view.add_provider_type, name='provider-type-add'),
    path('setting/general_settings/providerType/edit/<int:id>', views.general_view.edit_provider_type, name='provider-type-edit'),
    path('setting/general_settings/providerType/remove/<int:id>', views.general_view.delete_provider_type, name='provider-type-remove'),
    
    path('setting/general_settings/requiredDocument/add', views.general_view.add_required_document, name='required-document-add'),
    path('setting/general_settings/requiredDocument/edit/<int:id>', views.general_view.edit_required_document, name='required-document-edit'),
    path('setting/general_settings/requiredDocument/remove/<int:id>', views.general_view.delete_required_document, name='required-document-remove'),

    path('setting/general_settings/product/add', views.product_view.add_product_view, name='product-add'),
    path('setting/general_settings/product/edit/<int:id>', views.product_view.edit_product_view, name='product-edit'),
    path('setting/general_settings/product/remove/<int:id>', views.product_view.delete_product, name='product-remove'),
    
    path('save/log/call/', views.call_view.save_log_call, name="save_log_call"),
    
    # URLS CORRESPONDIENTES A LOS ENDPOINT 
    path('token/', views.call_view.get_token, name="get-token"),
    path('webcall/handle_calls/', views.call_view.call, name="call"),
    path('webcall/sms/reply/', views.call_view.sms_reply, name='sms-reply'),
    
    path('sms/', views.notify_view.sms, name="sms"),
    path('sms/<int:customer_id>/', views.notify_view.sms, name='sms_detail'),
    path('login=fail/', views.login_view.my_login_view, name="my_login_view"),
    path('logout/', views.login_view.logout_view, name="logout"),
    path('setting/users/', views.user_view.UserListView.as_view(), name="users"),
    path('setting/users/new/', views.user_view.create_user, name="new-user"),
    path('setting/users/edit/<int:user_id>/', views.user_view.edit_user, name="edit-user"),
    path('setting/users/password/reset/<int:user_id>/', views.user_view.reset_password, name="reset-password"),
    path('setting/users/remove/<int:user_id>/', views.user_view.delete_user, name="delete-user"),
    path('setting/company/edit', views.company_view.edit_company, name="company-edit"),
   
]
