from django.conf import settings
from .models import Product

class Cart:

    def add(self, product, quantity=1):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price), 'image_url': str(product.image.url)}
        self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            cart_item = self.cart[str(product.id)]
            cart_item['product'] = product
            cart_item['price'] = float(cart_item['price'])
            cart_item['total_price'] = cart_item['price'] * cart_item['quantity']
            yield cart_item

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()