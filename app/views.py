from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from django.shortcuts import render, redirect
from app.forms import RegisterForm, UploadUserProfilePicture, UpdateProfile, UpdatePassword, ProductForm, CommentForm, \
    ConfirmOrderForm

from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from app.models import User, Product, Follower, Comment, Cart, CartItem, Favorite
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse


# Create your views here.


def index(request):
    ls = Product.objects.all()
    try:
        user = User.objects.get(username=request.user.username)
        ls = Product.objects.exclude(user_id=user)
        followers = Follower.objects.filter(follower=user)

        FollowersId = [follower.followed for follower in followers]
        filtredProducts = Product.objects.filter(Q(user_id__in=FollowersId))

        excluded_ids = [follower.followed.id for follower in followers]
        excluded_ids.append(user.id)  # exclude the actual user products
        OthersProducts = Product.objects.exclude(Q(user_id__in=excluded_ids))

        show_modal = request.session.pop('show_modal', False)

        return render(request, 'index.html',
                      {'user': user, 'products': OthersProducts, 'filtredProducts': filtredProducts, 'show_modal': show_modal})
    except User.DoesNotExist:
        return render(request, 'index.html', {'user': None, 'products': ls, 'filtredProducts': None})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        print(form.errors)

        if form.is_valid():
            # Check if user already exists
            u = User.objects.filter(username=form.cleaned_data['username'])

            if u:
                return render(request, 'register.html', {'form': form, 'error': True})

            else:
                form.save()
                email = form.cleaned_data.get('email')
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')

                # Authenticate user then login
                user = authenticate(username=username, password=raw_password)
                auth_login(request, user)

                # Create user in our database
                user = User.objects.create(username=username, email=email, password=raw_password,
                                           name=form.cleaned_data['name'])
                user.save()

                return redirect('/')
        else:
            return render(request, 'register.html', {'form': form, 'error': True})
    else:
        form = RegisterForm()
        return render(request, 'register.html', {'form': form, 'error': False})



@login_required(login_url='/login')
def profile_settings(request):
    if request.method == 'GET':
        user = User.objects.get(username=request.user.username)
        image_form = UploadUserProfilePicture()
        profile_form = UpdateProfile(initial={'name': user.name, 'username': user.username, 'email': user.email,
                                              'description': user.description})
        password_form = UpdatePassword()
        return render(request, 'profile_settings.html', {'user': user, 'image_form': image_form,
                                                         'profile_form': profile_form, 'password_form': password_form})

    elif request.method == 'POST' and 'image' in request.FILES:
        print("POST")
        user = User.objects.get(username=request.user.username)
        image_form = UploadUserProfilePicture(request.POST, request.FILES)
        if image_form.is_valid():
            file = request.FILES['image']

            if file:
                user.image = file
                user.update_image(file)
                user.save()
                print(user.image)
                return redirect('/account/settings')
        else:
            image_form = UploadUserProfilePicture()
            print(image_form.errors)
            return render(request, 'profile_settings.html', {'user': user, 'image_form': image_form})

    elif request.method == 'POST' and 'profile_change' in request.POST:
        # get the form info
        user = User.objects.get(username=request.user.username)
        profile_form = UpdateProfile(request.POST)
        if profile_form.is_valid():
            if user.name != profile_form.cleaned_data['name']:
                user.name = profile_form.cleaned_data['name']
            if user.username != profile_form.cleaned_data['username']:
                user.username = profile_form.cleaned_data['username']
            if user.email != profile_form.cleaned_data['email']:
                user.email = profile_form.cleaned_data['email']
            if user.description != profile_form.cleaned_data['description']:
                user.description = profile_form.cleaned_data['description']
            user.save()
            # update user info auth
            request.user.username = profile_form.cleaned_data['username']
            request.user.email = profile_form.cleaned_data['email']
            request.user.save()
            return redirect('/account/settings')

    elif request.method == 'POST' and 'password_change' in request.POST:
        user = User.objects.get(username=request.user.username)
        password_form = UpdatePassword(request.POST)
        image_form = UploadUserProfilePicture()
        profile_form = UpdateProfile(initial={'name': user.name, 'username': user.username, 'email': user.email,
                                              'description': user.description})
        if password_form.is_valid():
            if user.password == password_form.cleaned_data['old_password']:
                if password_form.cleaned_data['new_password'] == password_form.cleaned_data['confirm_new_password']:
                    user.password = password_form.cleaned_data['new_password']
                    request.user.password = password_form.cleaned_data['new_password']
                    user.save()
                    print('Password changed successfully!')
                    return render(request, 'profile_settings.html', {'user': user, 'password_form': password_form,
                                                                     'image_form': image_form,
                                                                     'profile_form': profile_form,
                                                                     'success': 'Password changed successfully!'})
                else:
                    print('Passwords do not match!')
                    return render(request, 'profile_settings.html', {'user': user, 'password_form': password_form,
                                                                     'image_form': image_form,
                                                                     'profile_form': profile_form
                        , 'error': 'Passwords do not match!'})
            else:
                print('Wrong password!')
                return render(request, 'profile_settings.html', {'user': user, 'password_form': password_form,
                                                                 'image_form': image_form,
                                                                 'profile_form': profile_form
                    , 'error': 'Wrong password!'})
        else:
            return render(request, 'profile_settings.html', {'user': user, 'password_form': password_form,
                                                             'image_form': image_form,
                                                             'profile_form': profile_form,
                                                             'error': 'Invalid form!'})
    elif request.method == 'POST' and 'delete_account' in request.POST:
        user = User.objects.get(username=request.user.username)
        request.user.delete()
        user.delete()
        return redirect('/login')


@login_required(login_url='/login')
def sell(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user_id = User.objects.get(username=request.user.username)

            # Agora, associe a imagem ao produto
            if 'image' in request.FILES:
                product.image = request.FILES[
                    'image']  # 'image' deve corresponder ao nome do campo de arquivo no formulário

            product.save()  # Salve o produto com a imagem associada
            # Redirecionar para onde você desejar após a criação do produto
            return redirect('/')
    else:
        form = ProductForm()
    user = User.objects.get(username=request.user.username)

    return render(request, 'Sell.html', {'form': form, 'user': user})


@login_required(login_url='/login')
def profile(request):
    if request.method == "GET":
        user = User.objects.get(username=request.user.username)

        # get the followers
        followers = Follower.objects.filter(followed=user)
        followers_list = []
        for follower in followers:
            followers_list.append(follower.follower)

        # get the following
        following = Follower.objects.filter(follower=user)
        following_list = []
        for followed in following:
            following_list.append(followed.followed)

        # get user's products
        products = Product.objects.filter(user_id=user)

        return render(request, 'profile.html', {'user': user, 'followers': followers_list,
                                                'following': following_list, 'products': products})

    elif request.method == "POST":
        for i in request.POST:
            if 'delete_' in i:
                product_id = i.split('_')[1]
                product = Product.objects.get(id=product_id)
                product.delete()
                return redirect('/account/profile')

            if 'sold_' in i:
                product_id = i.split('_')[1]
                product = Product.objects.get(id=product_id)
                product.delete()
                user = User.objects.get(username=request.user.username)
                user.sold += 1
                user.save()
                return redirect('/account/profile')


@login_required(login_url='/login')
def product_settings(request, product_id):
    if request.method == "GET":
        user = User.objects.get(username=request.user.username)
        product = Product.objects.get(id=product_id)
        favorites = Favorite.objects.filter(product_id=product).count()

        return render(request, 'product_settings.html', {'product': product, 'user': user, 'favorites': favorites})


#    elif request.method == "POST":
#        product = Product.objects.get(id=product_id)
#        if 'delete' in request.POST:
#            product.delete()
#            return redirect('/account/profile')
#        elif 'update' in request.POST:
#            form = ProductForm(request.POST, request.FILES)
#            if form.is_valid():
#                product.title = form.cleaned_data['title']
#                product.description = form.cleaned_data['description']
#                product.price = form.cleaned_data['price']
#                product.category = form.cleaned_data['category']
#                product.image = request.FILES['image']
#                product.save()
#                return redirect('/account/profile')
#            else:
#                return render(request, 'product_settings.html', {'product': product, 'error': True})


@login_required(login_url='/login')
def add_to_cart(request, product_id):
    try:

        product = get_object_or_404(Product, id=product_id)
        user = User.objects.get(username=request.user.username)

        cart, created = Cart.objects.get_or_create(user=user)

        cart_item, created = CartItem.objects.get_or_create(product=product, user=user)

        if not created:
            pass

        else:
            cart_item.price = product.price
            cart.price += product.price

            cart.items.add(cart_item)
            cart_item.save()
            cart.save()

        return redirect('/')

    except Product.DoesNotExist:

        return redirect('pagina_de_erro')


@login_required(login_url='/login')
def viewCart(request):
    user = User.objects.get(username=request.user.username)
    cart, created = Cart.objects.get_or_create(user=user)

    price = round(cart.price,2)

    return render(request, 'cart.html', {'cart_items': cart.items.all(), 'cart': cart, 'price': price, 'user': user})


@login_required(login_url='/login')
@require_POST
def delete_from_cart(request, item_id):
    try:
        user = User.objects.get(username=request.user.username)

        cart = Cart.objects.get(user=user)
        cart_item = CartItem.objects.get(id=item_id)

        cart.price -= cart_item.price

        cart_item.delete()

        cart.save()

        return redirect('view_cart')



    except CartItem.DoesNotExist:
        return redirect('pagina_de_erro')  # Substitua 'pagina_de_erro' pelo nome da URL da página de erro apropriada


def product_page(request, product_id):
    if request.method == "GET":
        product = Product.objects.get(id=product_id)
        seller = User.objects.get(id=product.user_id.id)
        # get other products from the same seller, max 4
        other_products = Product.objects.filter(user_id=seller).exclude(id=product_id)[:4]

        # check if the user is logged in
        if User.objects.filter(username=request.user.username).exists():
            user = User.objects.get(username=request.user.username)
        # comment form
        comment_form = CommentForm()

        # get number of followers of the seller
        followers = Follower.objects.filter(followed=seller)
        followers_list = []
        for follower in followers:
            followers_list.append(follower.follower)

        # see if the user has favorited the product
        favorite = False
        if User.objects.filter(username=request.user.username).exists():
            if Favorite.objects.filter(user_id=user, product_id=product):
                favorite = True

        # update the seen counter
        product.seen += 1
        product.save()

        ratings = Comment.objects.filter(seller_id=seller)
        rating = 0
        for r in ratings:
            rating += r.rating
        if ratings.count() > 0:
            rating = rating / ratings.count()
            rating = round(rating, 1)

        if User.objects.filter(username=request.user.username).exists():
            return render(request, 'product_page.html',
                          {'product': product, 'user': user, 'seller': seller, 'other_products': other_products,
                           'favorite': favorite, 'followers': followers_list, 'comment_form': comment_form,
                           'rating': rating})

        return render(request, 'product_page.html',
                      {'product': product, 'user': None, 'seller': seller, 'other_products': other_products,
                       'favorite': favorite, 'followers': followers_list, 'comment_form': comment_form,
                       'rating': rating})

    elif request.method == "POST" and 'remove_favorite' in request.POST:
        user = User.objects.get(username=request.user.username)
        product = Product.objects.get(id=product_id)
        favorite = Favorite.objects.get(user_id=user, product_id=product)
        favorite.delete()
        return redirect('/product/' + str(product_id))

    elif request.method == "POST" and 'favorite' in request.POST:
        user = User.objects.get(username=request.user.username)
        product = Product.objects.get(id=product_id)
        favorite = Favorite.objects.create(user_id=user, product_id=product)
        favorite.save()
        return redirect('/product/' + str(product_id))

    elif request.method == "POST" and 'follow' in request.POST:
        user = User.objects.get(username=request.user.username)
        product = Product.objects.get(id=product_id)
        seller = User.objects.get(id=product.user_id.id)
        follow = Follower.objects.create(follower=user, followed=seller)
        follow.save()
        return redirect('/product/' + str(product_id))

    elif request.method == "POST" and 'unfollow' in request.POST:
        user = User.objects.get(username=request.user.username)
        product = Product.objects.get(id=product_id)
        seller = User.objects.get(id=product.user_id.id)
        follow = Follower.objects.get(follower=user, followed=seller)
        follow.delete()
        return redirect('/product/' + str(product_id))

    elif request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data['comment']
            rating = 0
            if 'rating_input' in request.POST:
                rating = request.POST['rating_input']

            product = Product.objects.get(id=product_id)
            user = User.objects.get(username=request.user.username)
            comment = Comment.objects.create(text=comment, user_id=user, product_id=product, rating=rating)
            comment.save()
            return redirect('/product/' + str(product_id))

        elif "deleteProduct" in request.POST:
            product_id = request.POST['deleteProduct']
            Product.objects.filter(id=product_id).delete()
            return redirect('/adminpage/')  # Redirect to the desired page after deletion

        elif "deleteComment" in request.POST:
            comment_id = request.POST["deleteComment"]
            comment = Comment.objects.get(id=comment_id)
            comment.delete()
            return redirect('/product/' + str(product_id))

    return render(request, 'product_page.html')


def seller(request, username):
    if request.method == "GET":
        if username == request.user.username:
            return redirect('/account/profile')
        user = User.objects.get(username=username)
        # get the followers
        followers = Follower.objects.filter(followed=user)
        followers_list = []
        for follower in followers:
            followers_list.append(follower.follower)

        # get the following
        following = Follower.objects.filter(follower=user)
        following_list = []
        for followed in following:
            following_list.append(followed.followed)

        # get user's products
        products = Product.objects.filter(user_id=user)

        # get favorites
        favorites = Favorite.objects.filter(user_id=User.objects.get(username=request.user.username))
        favorites_list = []
        for favorite in favorites:
            favorites_list.append(favorite.product_id)

        # comment form
        comment_form = CommentForm()

        # get comments
        comments = Comment.objects.filter(user_id=User.objects.get(username=request.user.username),
                                          seller_id=user).order_by('-id')[:10]

        return render(request, 'seller.html', {'user': User.objects.get(username=request.user.username), 'seller': user,
                                               'followers': followers_list,
                                               'following': following_list, 'products': products,
                                               'favorites': favorites_list, 'comment_form': comment_form,
                                               'comments': comments})

    elif request.method == "POST" and 'follow' in request.POST:
        user = User.objects.get(username=username)
        follower = User.objects.get(username=request.user.username)
        follow = Follower.objects.create(follower=follower, followed=user)
        follow.save()
        return redirect('/profile/' + username)

    elif request.method == "POST" and 'unfollow' in request.POST:
        user = User.objects.get(username=username)
        follower = User.objects.get(username=request.user.username)
        follow = Follower.objects.get(follower=follower, followed=user)
        follow.delete()
        return redirect('/profile/' + username)

    elif request.method == "POST" and 'favorite' in request.POST:
        user = User.objects.get(username=request.user.username)
        product = Product.objects.get(id=request.POST['favorite'])
        if Favorite.objects.filter(user_id=user, product_id=product):
            favorite = Favorite.objects.get(user_id=user, product_id=product)
            favorite.delete()
            # this is returning to an ajax call
            data = {"message": "remove"}
            return JsonResponse(data)
        favorite = Favorite.objects.create(user_id=user, product_id=product)
        favorite.save()
        # this is returning to an ajax call
        data = {"message": "add"}
        return JsonResponse(data)

    elif request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data['comment']
            rating = 0
            if 'rating_input' in request.POST:
                rating = request.POST['rating_input']

            user = User.objects.get(username=request.user.username)
            seller = User.objects.get(username=username)
            comment = Comment.objects.create(text=comment, user_id=user, seller_id=seller, rating=rating)
            comment.save()
            return redirect('/profile/' + username)

        elif "deleteComment" in request.POST:
            comment_id = request.POST["deleteComment"]
            comment = Comment.objects.get(id=comment_id)
            comment.delete()
            return redirect('/profile/' + username)
        # Add a default response here, or handle other cases as needed
        return HttpResponse("Some default response")






def admin_page(request):
    errorUser = False
    errorProduct = False
    user = User.objects.get(username=request.user.username)

    if request.method == "GET":
        user = User.objects.get(username=request.user.username)
        if user.admin:
            users = User.objects.all()
            products = Product.objects.all()
            return render(request, 'admin_page.html', {'user': user, 'users': users, 'products': products})
        else:
            return redirect('/')

    if request.method == "POST":
        if "searchUser" in request.POST:
            q = request.POST['searchUser']
            if q:
                users = User.objects.filter(username__icontains=q)
                if users.exists():
                    user = users.first()
                    products = Product.objects.all()
                    errorUser = False
                else:
                    users = User.objects.all()
                    products = Product.objects.all()
                    errorUser = True
            else:
                users = User.objects.all()
                products = Product.objects.all()
            return render(request, 'admin_page.html',
                          {'user': user, 'users': users, 'products': products, 'errorUser': errorUser, 'errorProduct': errorProduct})

        elif "searchProduct" in request.POST:
            q = request.POST['searchProduct']
            users = User.objects.all()
            if q:
                products_by_name = Product.objects.filter(name__icontains=q)
                products_by_user = Product.objects.filter(user_id__username__icontains=q)
                products = products_by_name.union(products_by_user)
                if not products.exists():
                    products = Product.objects.all()
                    errorProduct = True
                else:
                    errorProduct = False
            else:
                products = Product.objects.all()
                errorProduct = False
            return render(request, 'admin_page.html',
                          {'user': user, 'users': users, 'products': products, 'errorUser': errorUser, 'errorProduct': errorProduct})

        elif "deleteUser" in request.POST:
            user_id = request.POST['deleteUser']
            User.objects.filter(id=user_id).delete()
            Product.objects.filter(user_id=user_id).delete()
        elif "deleteProduct" in request.POST:
            product_id = request.POST['deleteProduct']
            Product.objects.filter(id=product_id).delete()

    users = User.objects.all()
    products = Product.objects.all()
    return render(request, 'admin_page.html',
                  {'user': user, 'errorUser': errorUser, 'errorProduct': errorProduct, 'users': users, 'products': products})


@login_required(login_url='/login')
def edit_product(request, product_id):
    # if the user is not the owner of the product, redirect to the product page
    product = Product.objects.get(id=product_id)
    if request.user.username != product.user_id.username:
        return redirect('/product/' + str(product_id))

    if request.method == "GET":
        form = ProductForm(initial={'name': product.name, 'description': product.description, 'price': product.price,
                                    'image': product.image, 'brand': product.brand, 'category': product.category,
                                    'color': product.color})
        return render(request, 'edit_product.html', {'form': form, 'product': product})

    elif request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product.name = form.cleaned_data['name']
            product.description = form.cleaned_data['description']
            product.price = form.cleaned_data['price']
            product.category = form.cleaned_data['category']
            product.brand = form.cleaned_data['brand']
            product.color = form.cleaned_data['color']

            # Agora, associe a imagem ao produto
            if 'image' in request.FILES:
                product.image = request.FILES[
                    'image']

            product.save()
            return redirect('/account/product/' + str(product_id))
        else:
            return render(request, 'edit_product.html', {'form': form, 'product': product, 'error': True})


def process_payment(request):
    user = User.objects.get(username=request.user.username)
    cart, created = Cart.objects.get_or_create(user=user)
    price = round(cart.price, 2)
    if request.method == 'POST':
        form = ConfirmOrderForm(request.POST)
        if form.is_valid():
            cart.items.all().delete()
            cart.price = 0
            cart.save()
            request.session['show_modal'] = True

            return HttpResponseRedirect(reverse('index'))
    else:
        form = ConfirmOrderForm()

    return render(request, 'process_payment.html',
                  {'cart_items': cart.items.all(), 'cart': cart, 'user': user, 'form': form, 'price': price})


@login_required(login_url='/login')
def favorites(request):
    # Get the user
    user = request.user

    # Get the user ID
    user = User.objects.get(username=user.username)

    # Get the favorites for the user
    favorites = Favorite.objects.filter(user_id=user)

    # Get the product IDs from the favorites
    favorites_product_ids = [favorite.product_id.id for favorite in favorites]

    # Get the products that match the IDs
    favorites_products = Product.objects.filter(id__in=favorites_product_ids)


    return render(request, 'favorites.html',
                  {'favorites': favorites_products, 'user': user})
