from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("categoryitems/<str:category>", views.categoryitems, name="categoryitems"),
    path("create", views.create, name="create"),
    path("listings/<int:id>",views.listingpage,name="listingpage"),
    path("watchlist",views.watchlistpage,name="watchlistpage"),
    path("addwatchlist/<int:listingid>",views.addwatchlist,name="addwatchlist"),
    path("removewatchlist/<int:listingid>",views.removewatchlist,name="removewatchlist"),
    path("closebid/<int:listingid>",views.closebid,name="closebid"),
    path("bidsubmit/<int:listingid>",views.bidsubmit,name="bidsubmit"),
    path("cmntsubmit/<int:listingid>",views.cmntsubmit,name="cmntsubmit"),
    path("submit",views.submit,name="submit"),
    path("mywinnings",views.mywinnings,name="mywinnings")
]
