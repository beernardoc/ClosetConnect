from django.db import models


# Create your models here.
class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=70)
    name = models.CharField(max_length=70)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    admin = models.BooleanField(default=False)
    image = models.FileField()
    description = models.TextField(null=True, blank=True)
    sold = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def update_image(self, file):
        self.image.storage.delete(self.image.name)
        self.image = file


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=70)
    description = models.TextField(null=True, blank=True)
    price = models.FloatField(max_length=10, default=0.00)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    seen = models.IntegerField(default=0)
    brand = models.CharField(max_length=70, null=True, blank=True)
    category = models.CharField(max_length=70, null=True, blank=True)
    color = models.CharField(max_length=70, null=True, blank=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField(null=True, blank=True)
    rating = models.IntegerField(default=0)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    seller_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller')

    def __str__(self):
        return self.text



class Follower(models.Model):
    id = models.AutoField(primary_key=True)
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed')

    def __str__(self):
        return self.follower.name + " follows " + self.followed.name


class Favorite(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.user_id.name + " likes " + self.product_id.name


class CartItem(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField(max_length=10, default=0.00)

    def __str__(self):
        return f"{self.product.name}, Price: {self.price}"


class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(CartItem)
    price = models.FloatField(max_length=10, default=0.00)

    def __str__(self):
        return self.items.all().__str__() + " in Cart " + str(self.id) + " of " + self.user.name


