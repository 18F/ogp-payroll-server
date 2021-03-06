"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers

from fpds.views import get_fpds
from payrolls.views import (
    ContractorViewSet, DayViewSet, FringeExceptionViewSet, LineQuantityViewSet,
    LocationViewSet, PayrollLineViewSet, PayrollUploadViewSet, PayrollViewSet,
    ProjectContractorViewSet, ProjectViewSet, UserDetail, UserList,
    WorkerViewSet, WorkweekViewSet)
from sam.views import get_sam
from wage_determinations.views import (CountyViewSet, RateSearchList,
                                       RateViewSet, StateViewSet,
                                       WageDeterminationViewSet)

router = routers.DefaultRouter()
router.register(r'county', CountyViewSet)
router.register(r'state', StateViewSet)
router.register(r'contractor', ContractorViewSet)
router.register(r'location', LocationViewSet)
router.register(r'project', ProjectViewSet)
router.register(r'project_contractor', ProjectContractorViewSet)
router.register(r'payroll', PayrollViewSet)
router.register(r'worker', WorkerViewSet)
router.register(r'workweek', WorkweekViewSet)
router.register(r'payroll_line', PayrollLineViewSet)
router.register(r'day', DayViewSet)
router.register(r'line-quantity', LineQuantityViewSet)
router.register(r'fringe-exception', FringeExceptionViewSet)
router.register(r'payrollupload', PayrollUploadViewSet)
router.register(r'wage-determination', WageDeterminationViewSet)
router.register(r'rate', RateViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/',
        include('rest_framework.urls',
                namespace='rest_framework')),
    url(r'^users/$', UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$',
        UserDetail.as_view(),
        name='user-detail'),
    # url(r'^payrolls/upload$', PayrollUpload.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', UserDetail.as_view()),
    url(r'^rate/search', RateSearchList.as_view()),
    url(r'^contract/(?P<contract_no>[0-9A-Z]+)/$',
        get_fpds,
        name='fpds'),
    url(r'^contractor/(?P<duns>[0-9A-Z]+)/$',
        get_sam,
        name='sam'),
]
