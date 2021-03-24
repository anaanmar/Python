from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import User, Bid, Listing, Comment, Watchlist
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Max


def index(request):
    items = Listing.objects.exclude(active=False).all()
    #items = Listing.objects.all()
    if items :
        for i in items :
            try:
                current_bid = int(Bid.objects.filter(
                listingid=i.id).aggregate(Max('bid'))['bid__max'] )
                
            except:
                current_bid = i.price
            i.price = current_bid
    try:
        wlist = Watchlist.objects.filter(userid=request.user.id)
        wcount = len(wlist)
    except:
        wlist = None
        wcount = 0
    return render(request, "auctions/index.html", {
        "items": items,
        "wcount": wcount
    })


def categories(request):
    categories = Listing.objects.raw(
        "SELECT * FROM auctions_listing GROUP BY category")
    #categories = Listing.objects.all().distinct('category')

    try:
        wlist = Watchlist.objects.filter(userid=request.user.id)
        wcount = len(wlist)
    except:
        wcount = 0
    return render(request, "auctions/category.html", {
        "categories": categories,
        "wcount": wcount
    })


def categoryitems(request, category):
    catitems = Listing.objects.filter(category=category, active=True)
    if catitems :
        for i in catitems :
            try:
                current_bid = int(Bid.objects.filter(
                listingid=i.id).aggregate(Max('bid'))['bid__max'] )
                
            except:
                current_bid = i.price
            i.price = current_bid
    try:
        wlist = Watchlist.objects.filter(userid=request.user.id)
        wcount = len(wlist)
    except:
        wcount = 0
    return render(request, "auctions/categoryitems.html", {
        "items": catitems,
        "category": category,
        "wcount": wcount
    })


@login_required(login_url='/login', redirect_field_name='')
def create(request):
    try:
        wlist = Watchlist.objects.filter(userid=request.user.id)
        wcount = len(wlist)
    except:
        wcount = 0
    return render(request, "auctions/create.html", {
        "wcount": wcount
    })


@login_required(login_url='/login', redirect_field_name='')
def submit(request):
    if request.method == "POST":
        listtable = Listing()
        listtable.owner = request.user
        listtable.title = request.POST.get('title')
        listtable.description = request.POST.get('description')
        listtable.price = request.POST.get('price')
        listtable.category = request.POST.get('category')
        if request.POST.get('link'):
            listtable.link = request.POST.get('link')
        else:
            listtable.link = "https://wallpaperaccess.com/full/1605486.jpg"
        listtable.save()

        return redirect('index')
    else:
        return redirect('index')


def listingpage(request, id):
    try:
        item = Listing.objects.get(id=id, active=True)
    except:
        return redirect('index')

    try:
        comments = Comment.objects.filter(listingid=id)
    except:
        comments = None

    if request.user.id:
        try:
            if Watchlist.objects.get(userid=request.user.id, listingid=id):
                added = True
        except:
            added = False
        try:
            l = Listing.objects.get(id=id, active=True)
            u = User.objects.get(username=l.owner)
            if u.id == request.user.id:
                owner = True
            else:
                owner = False
        except:
            return redirect('index')
    else:
        added = False
        owner = False
    try:
        w = Watchlist.objects.filter(userid=request.user.id)
        wcount = len(w)
    except:
        wcount = None

    try:
        bids = Bid.objects.filter(listingid=id)
        max_bid = Bid.objects.filter(listingid=id).aggregate(Max('bid'))
        #max_bid = 55
        bids_count = len(bids)
        #is_winner = True
        last_bid = item.price
        winner = Bid.objects.get(
            listingid=id, closed=False, bid=max_bid['bid__max'])

        if winner.userid == request.user:
            is_winner = True
            last_bid = winner.bid
        else:
            is_winner = False
            last_bid = winner.bid

    except:
        is_winner = False
        bids_count = 0
        last_bid = item.price

    return render(request, "auctions/listingpage.html", {
        "i": item,
        "error": request.COOKIES.get('error'),
        "errorgreen": request.COOKIES.get('errorgreen'),
        "comments": comments,
        "added": added,
        "owner": owner,
        "wcount": wcount,
        "is_winner": is_winner,
        "last_bid": last_bid,
        "bids_count": bids_count
    })


@login_required(login_url='/login', redirect_field_name='')
def watchlistpage(request):

    userwlist = Watchlist.objects.filter(userid=request.user)
    items = []
    for i in userwlist:
        if i.listingid.active:
            
            try:
                current_bid = int(Bid.objects.filter(
                listingid=i.listingid.id).aggregate(Max('bid'))['bid__max'] )
                
            except:
                current_bid = i.listingid.price
            i.listingid.price = current_bid
            items.append(i.listingid)

    wlist = Watchlist.objects.filter(userid=request.user.id)
    wcount = len(wlist)
    #items = userwlist.listingid.all()
    return render(request, "auctions/watchlistpage.html", {
        "items": items,
        "wcount": len(userwlist)
    })


@login_required(login_url='/login', redirect_field_name='')
def mywinnings(request):
    won_bids = Bid.objects.values('listingid').annotate(maxbid = Max('bid')).filter(userid=request.user , closed=True)
    # won_bids = Bid.objects.filter(
    #     userid=request.user, closed=True).annotate(Max('bid'))
    wonitems = []
    if won_bids:
        for i in won_bids:
            item = Listing.objects.get(id=i['listingid'])
            t = {'title' : item.title , 'description' : item.description , 'price' :i['maxbid'] , 'link' : item.link }
            wonitems.append(t)
    else:
        wonitems = None
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        wcount = len(w)
    except:
        wcount = 0
    return render(request, 'auctions/mywinnings.html', {
        "wcount": wcount,
        "wonitems": wonitems
    })


@login_required(login_url='/login', redirect_field_name='')
def addwatchlist(request, listingid):
    w = Watchlist()
    w.userid = request.user
    w.listingid = Listing.objects.get(id=listingid)
    w.save()
    return redirect('listingpage', id=listingid)


@login_required(login_url='/login', redirect_field_name='')
def removewatchlist(request, listingid):
    w = Watchlist.objects.get(
        userid=request.user, listingid=Listing.objects.get(id=listingid))
    w.delete()
    return redirect('listingpage', id=listingid)


@login_required(login_url='/login', redirect_field_name='')
def closebid(request, listingid):
    try:
        item = Listing.objects.get(id=listingid)
    except:
        return redirect('index')

    try:
        bids = Bid.objects.filter(listingid=item, closed=False)
        for bid in bids:
            bid.closed = True
            bid.save()
        item.active = False
        item.save()
        wlist = Watchlist.objects.filter(listingid=item)
        wlist.delete()
        comments = Comment.objects.filter(listingid=item)
        comments.delete()
    except:
        item.active = False
        item.save()
        wlist = Watchlist.objects.filter(listingid=item)
        wlist.delete()
        comments = Comment.objects.filter(listingid=item)
        comments.delete()
    return redirect('index')


@login_required(login_url='/login', redirect_field_name='')
def bidsubmit(request, listingid):
    current_item = Listing.objects.get(id=listingid)
    current_bid = current_item.price - 1
    try:
        current_bid = int(Bid.objects.filter(
            listingid=listingid).aggregate(Max('bid'))['bid__max'] )
    except:
        current_bid = current_item.price - 1
    #current_bid = current_item.price
    if request.method == "POST":
        user_bid = int(request.POST.get("bid"))
        if user_bid > current_bid:
            #current_item.price = user_bid
            #current_item.save()
            # if Bid.objects.filter(id=listingid,closed=False):
            #         bidrow = Bid.objects.filter(id=listingid)
            #         bidrow.delete()
            bidtable = Bid()
            bidtable.userid = request.user
            bidtable.listingid = current_item
            bidtable.bid = user_bid
            bidtable.save()
            response = redirect('listingpage', id=listingid)
            response.set_cookie('errorgreen', 'bid successful!!!', max_age=3)
            return response
        else:
            response = redirect('listingpage', id=listingid)
            response.set_cookie(
                'error', f'Bid should be greater than current price ', max_age=3)
            return response
    else:
        return redirect('index')


@login_required(login_url='/login', redirect_field_name='')
def cmntsubmit(request, listingid):
    try:
        item = Listing.objects.get(id=listingid)
    except:
        return redirect('index')
    if request.method == "POST":
        c = Comment()
        c.comment = request.POST.get('comment')
        c.userid = request.user
        c.listingid = item
        c.save()
        return redirect('listingpage', id=listingid)
    else:
        return redirect('index')


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
