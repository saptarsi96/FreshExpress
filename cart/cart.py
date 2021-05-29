class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = request.session.get('cart')
        order=request.session.get('order')
        if(not cart):
            cart = self.session['cart']={}
        self.cart = cart
        if(not order):
            order=self.session['order']={'order':"NULL"}
        self.order=order

    def addorder(self,orderid):
        self.order['order']=orderid
        self.save()

    def getorder(self):
        return self.order['order']

    def removeorder(self):
        self.order['order']="NULL"
        self.save()

    def add(self, productid, price, quantity=1):
        if(quantity == 0):
            self.remove(productid)
            return
        self.cart[productid] = {'quantity': quantity, 'price': price}
        self.save()
        self.removeorder()

    def remove(self, productid):
        if(productid in self.cart):
            del self.cart[productid]
            self.save()
        self.removeorder()        

    def save(self):
        self.session.modified = True

    def get_total_price(self):
        return sum(i['quantity']*i['price'] for i in self.cart.values())

    def __len__(self):
        return sum(i['quantity'] for i in self.cart.values())

    def empty(self):
        return len(self.cart) == 0

    def clear(self):
        del self.session['cart']
        del self.session['order']


    def keys(self):
        return map(lambda k: int(k), self.cart.keys())

    def __getitem__(self, arg):
        if isinstance(arg, str):
            return self.cart[arg]['quantity']
        raise TypeError('Slicing cart is not allowed.')


def cart_preprocessor(request):
    return {'cart': Cart(request)}
