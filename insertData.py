import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TPW_project_1.settings")
django.setup()

from app.models import User, Product, Comment, Follower, Favorite
from django.contrib.auth import authenticate, login as auth_login


# Crie o primeiro usuário
user1 = User.objects.create(
    username='joao',
    name='joao',
    email='joao@example.com',
    password='user1234',  # Você deve usar um método seguro para armazenar senhas reais
    admin=False,  # Este usuário é um administrador
    image='users/joao.png',
    sold=23
)
authenticate(username='joao', password='user1234')


# Crie o segundo usuário
user2 = User.objects.create(
    username='jose',
    name='jose',
    email='jose@example.com',
    password='user1234',  # Você deve usar um método seguro para armazenar senhas reais
    admin=False,  # Este usuário não é um administrador
    image='users/jose.png',
    sold=12
)
authenticate(username='jose', password='user1234')

user3 = User.objects.create(
    username='manel123',
    name='Manuel',
    email='manel@example.com',
    password='user1234',  # Você deve usar um método seguro para armazenar senhas reais
    admin=True,  # Este usuário não é um administrador
)
authenticate(username='jose', password='user1234')


products = [
    Product(name='T-shirt Estampada', description='T-shirt de algodão estampada', price=29.99, user_id=user1, brand='Nike', category='Clothing', color='White',
            seen=10, image='product_images/tshirt.jpg'),
    Product(name='Tênis Desportivo', description='Tênis desportivo de alta qualidade', price=59.99, user_id=user1, brand='Nike', category='Shoes', color='Black',
            seen=20, image='product_images/shoes.jpg'),
    Product(name='Relógio Elegante', description='Relógio de pulso elegante', price=49.99, user_id=user1, brand='Rolex', category='Watches', color='Black',
            seen=30, image='product_images/rolex.jpg'),
    Product(name='Chapéu de Beisebol', description='Chapéu de beisebol clássico', price=14.99, user_id=user1, brand='Adidas', category='Hats', color='Bordeaux',
            seen=4, image='product_images/cap.jpg'),
    Product(name='Mochila Resistente', description='Mochila resistente para viagens', price=39.99, user_id=user2, brand='Eastpak', category='Bags', color='Black',
            seen=5, image='product_images/mochila.jpg'),
    Product(name='Sapatos Formais', description='Sapatos de couro para ocasiões formais', price=69.99, user_id=user2, brand='Clarks', category='Shoes', color='Brown',
            seen=6, image='product_images/formal.jpg'),
    Product(name='Casaco de Inverno', description='Casaco quente para inverno', price=79.99, user_id=user2, brand='North Face', category='Clothing', color='Black',
            seen=7, image='product_images/casaco.jpg'),
    Product(name='Calça Jeans Moderna', description='Calça jeans moderna e confortável', price=34.99, user_id=user2, brand='Levis', category='Clothing', color='Blue',
            seen=8, image='product_images/calcas.jpg'),
    Product(name='Óculos de Sol Fashion', description='Óculos de sol na moda', price=19.99, user_id=user2, brand='Ray-Ban', category='Glasses', color='Black',
            seen=9, image='product_images/oculos.jpeg'),
    Product(name='Bolsa Elegante', description='Bolsa elegante para mulheres', price=44.99, user_id=user2, brand='Michael Kors', category='Bags', color='Black',
            seen=10, image='product_images/bag.jpg'),
]

for p in products:
    p.save()

comments = [
    Comment(text='Ótimos produtos', rating=5, user_id=user1, seller_id=user2),
    Comment(text='Produtos de alta qualidade', rating=4, user_id=user1, seller_id=user2),
    ]

for c in comments:
    c.save()

followers = [
    Follower(follower=user1, followed=user2),
    Follower(follower=user2, followed=user1),
    ]

for f in followers:
    f.save()

favorites = [
    Favorite(user_id=user2, product_id=products[0]),
    Favorite(user_id=user2, product_id=products[1]),
    Favorite(user_id=user1, product_id=products[-1]),
    ]

for f in favorites:
    f.save()