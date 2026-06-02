from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import models
from database import engine, get_db

# Автоматически создаем таблицы в PostgreSQL, если их нет
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Подключаем статику и шаблоны
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# =====================================================================
# БЕЗОПАСНОСТЬ И ОБРАБОТЧИКИ
# =====================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Критическая ошибка системы: {exc}")
    return templates.TemplateResponse(
        request=request,
        name="error.html", 
        context={"message": "Произошла внутренняя ошибка системы."},
        status_code=500
    )


# =====================================================================
# МАРШРУТЫ: АВТОРИЗАЦИЯ
# =====================================================================

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={"error": None})


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or user.password_hash != password:
        return templates.TemplateResponse(request=request, name="login.html", context={"error": "Неверный логин или пароль."})
    
    response = RedirectResponse(url="/products", status_code=303)
    response.set_cookie(key="user_id", value=str(user.id))
    response.delete_cookie("user_role")
    return response


@app.get("/logout")
@app.post("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("user_id")
    response.delete_cookie("user_role")
    return response


# =====================================================================
# МАРШРУТЫ: УПРАВЛЕНИЕ ТОВАРАМИ (ДОБАВЛЕНИЕ/УДАЛЕНИЕ)
# =====================================================================

@app.get("/add_product", response_class=HTMLResponse)
def show_add_form(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id: return RedirectResponse(url="/")
    
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user or user.role.name != 'Администратор':
        return RedirectResponse(url="/products")
    
    return templates.TemplateResponse(request=request, name="product_form.html", context={
        "categories": db.query(models.Category).all(),
        "manufacturers": db.query(models.Manufacturer).all(),
        "suppliers": db.query(models.Supplier).all(),
        "units": db.query(models.Unit).all()
    })

@app.post("/add_product")
def add_product(request: Request, name: str = Form(...), description: str = Form(None), price: float = Form(...),
                stock_quantity: int = Form(...), discount: int = Form(0), category_id: int = Form(...),
                manufacturer_id: int = Form(...), supplier_id: int = Form(...), unit_id: int = Form(...),
                db: Session = Depends(get_db)):
    
    user_id = request.cookies.get("user_id")
    if not user_id: return RedirectResponse(url="/")
        
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user or user.role.name != 'Администратор': return RedirectResponse(url="/products")

    new_product = models.Product(name=name, description=description, price=price, stock_quantity=stock_quantity,
                                 discount=discount, category_id=category_id, manufacturer_id=manufacturer_id,
                                 supplier_id=supplier_id, unit_id=unit_id)
    db.add(new_product)
    db.commit()
    return RedirectResponse(url="/products", status_code=303)

@app.post("/delete_product/{product_id}")
def delete_product(product_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id: return RedirectResponse(url="/", status_code=303)
    
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user or user.role.name != 'Администратор': return RedirectResponse(url="/products", status_code=303)

    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
    
    return RedirectResponse(url="/products", status_code=303)


# =====================================================================
# МАРШРУТ: ПРОСМОТР ТОВАРОВ
# =====================================================================

@app.get("/products", response_class=HTMLResponse)
def get_products(request: Request, db: Session = Depends(get_db)):
    current_user = {"full_name": "Гость", "role": "Гость"}
    
    user_id = request.cookies.get("user_id")
    if user_id:
        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        if user:
            current_user = {"full_name": user.full_name, "role": user.role.name}
            
    products_db = db.query(models.Product).all()
    products = []
    
    for p in products_db:
        p_price = float(p.price)
        final_price = round(p_price * (1 - p.discount / 100), 2)
        
        products.append({
            "id": p.id,  # ОЧЕНЬ ВАЖНО ДЛЯ КНОПКИ УДАЛЕНИЯ
            "name": p.name,
            "description": p.description,
            "price": p_price,
            "discount": p.discount,
            "final_price": final_price,
            "stockQuantity": p.stock_quantity, # Используем camelCase для соответствия шаблону
            "category": p.category.name if p.category else 'Общая',
            "manufacturer": p.manufacturer.name if p.manufacturer else 'Не указан',
            "imagePath": p.image_path # Используем название из модели
        })
    
    return templates.TemplateResponse(request=request, name="products.html", 
                                      context={"user": current_user, "products": products})
# запускать через py -m uvicorn main:app --reload