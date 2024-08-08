# models.py
from django.db import models
from django.contrib.auth.models import User

CATEGORY_CHOICES = (
    ('V', 'Vegetables'),
    ('F', 'Fruits'),
    ('J', 'Juices')
)
    

class Category(models.Model):
    name = models.CharField(max_length=200)
    CATEGORY_CHOICES = [('Vegetables','Vegetables'),('Fruits','Fruits'),('Juices','Juices')]

    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    image = models.ImageField(upload_to='products/',blank=True, null=True)
    

    def __str__(self):
        return f"{self.name}"
    


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
  

    class Meta:
        unique_together = ('user', 'product')

User.add_to_class('wishlist', models.ManyToManyField(Product, through=Wishlist, related_name='wishlisted_by'))     
    


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart of {self.user.username}"



class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}"

    def get_item_name(self):
        if self.product:
            return self.product.name
        return self.product.name
    
    @property
    def total(self):
        if self.product:
            return self.product.price * self.quantity
        return 0  



class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id}"
    
    @property
    def total_cost(self):
        return sum(item.price for item in self.items.all())

class OrderItems(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product if self.product else self.mobile}"       