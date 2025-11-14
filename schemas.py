"""
Схемы валидации данных с использованием Marshmallow
"""
from marshmallow import Schema, fields, validate, ValidationError as MarshmallowValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import User, Product, Category, Order, OrderItem, Work, PasswordResetCode, Brand

# ========== User Schemas ==========
class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)

class UserRegisterSchema(Schema):
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6, max=100))

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UserUpdateSchema(Schema):
    first_name = fields.Str(validate=validate.Length(min=1, max=120))
    last_name = fields.Str(validate=validate.Length(min=1, max=120))
    email = fields.Email()

class ChangePasswordSchema(Schema):
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6, max=100))

class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)

class VerifyCodeSchema(Schema):
    email = fields.Email(required=True)
    code = fields.Str(required=True, validate=validate.Length(min=6, max=6))

class ResetPasswordSchema(Schema):
    email = fields.Email(required=True)
    code = fields.Str(required=True, validate=validate.Length(min=6, max=6))
    new_password = fields.Str(required=True, validate=validate.Length(min=6, max=100))

# ========== Product Schemas ==========
class ProductSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        include_relationships = True

class ProductCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(allow_none=True)
    price = fields.Float(required=True, validate=validate.Range(min=0))
    stock = fields.Int(validate=validate.Range(min=0), missing=0)
    category_id = fields.Int(allow_none=True)
    brand_id = fields.Int(allow_none=True)

class ProductUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1, max=200))
    description = fields.Str(allow_none=True)
    price = fields.Float(validate=validate.Range(min=0))
    stock = fields.Int(validate=validate.Range(min=0))
    category_id = fields.Int(allow_none=True)
    brand_id = fields.Int(allow_none=True)

# ========== Category Schemas ==========
class CategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        load_instance = True

# ========== Order Schemas ==========
class OrderItemSchema(SQLAlchemyAutoSchema):
    product = fields.Nested(ProductSchema, dump_only=True)
    
    class Meta:
        model = OrderItem
        load_instance = True
        include_relationships = True

class OrderSchema(SQLAlchemyAutoSchema):
    items = fields.Nested(OrderItemSchema, many=True, dump_only=True)
    user = fields.Nested(UserSchema, dump_only=True)
    
    class Meta:
        model = Order
        load_instance = True
        include_relationships = True

# ========== Cart Schemas ==========
class CartAddSchema(Schema):
    product_id = fields.Int(required=True, validate=validate.Range(min=1))
    quantity = fields.Int(validate=validate.Range(min=1), missing=1)

class CartUpdateSchema(Schema):
    product_id = fields.Int(required=True, validate=validate.Range(min=1))
    quantity = fields.Int(required=True, validate=validate.Range(min=0))

class CartRemoveSchema(Schema):
    product_id = fields.Int(required=True, validate=validate.Range(min=1))

# ========== Work Schemas ==========
class WorkSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Work
        load_instance = True

class WorkCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    image = fields.Str(required=True)
    link = fields.Str(missing='#')

# ========== Query Parameter Schemas ==========
class ProductListQuerySchema(Schema):
    q = fields.Str(allow_none=True)
    category = fields.Int(allow_none=True, validate=validate.Range(min=1))
    brand_id = fields.Int(allow_none=True, validate=validate.Range(min=1))
    min_price = fields.Float(allow_none=True, validate=validate.Range(min=0))
    max_price = fields.Float(allow_none=True, validate=validate.Range(min=0))
    sort = fields.Str(
        validate=validate.OneOf(['price_asc', 'price_desc', 'title_asc', 'title_desc', 'id_desc', 'newest']),
        missing='id_desc'
    )
    page = fields.Int(validate=validate.Range(min=1), missing=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), missing=12)

class WorksListQuerySchema(Schema):
    page = fields.Int(validate=validate.Range(min=1), missing=1)
    limit = fields.Int(validate=validate.Range(min=1, max=100), missing=12)

