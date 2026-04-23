from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('hr/', include(('hr.urls', 'hr'), namespace='hr')),
    path('gm/', include(('gm.urls', 'gm'), namespace='gm')),
    path('manager/', include(('manager.urls', 'manager'), namespace='manager')),
    
    # New Team Lead App
    path('teamlead/', include(('teamlead.urls', 'teamlead'), namespace='teamlead')),
    
    # Placeholder for BDE (Uncomment when you create the bde app)
    # path('bde/', include(('bde.urls', 'bde'), namespace='bde')),
    path('bde/', include('bde.urls')),
]