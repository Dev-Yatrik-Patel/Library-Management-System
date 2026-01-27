from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc

from app.schemas.book import BookCreate, BookUpdate

from app.models.book import Book

from app.exceptions.book import BookNotFound

def create_book_admin(book: BookCreate, db: Session):
    db_book_obj = Book(
        name = book.name,
        isbn = book.isbn,
        stock = book.stock
    )
    db.add(db_book_obj)
    db.commit()
    db.refresh(db_book_obj)
    
    return db_book_obj

def search_books(
    search: str | None
    ,in_stock: bool | None
    ,sort_by: str
    ,order: str
    ,page: int 
    ,limit: int
    ,db: Session
    ):
    
    query = db.query(Book)
    
    # searching 
    if search:
        query = query.filter( or_ 
                             (
                                 Book.name.ilike(f"%{search}%"),
                                 Book.isbn.ilike(f"%{search}%")
                             )
                            )
    # in stock filter
    if in_stock is True:
        query = query.filter(Book.stock > 0) 
    
    # sorting column
    if sort_by == "stock":
        sort_column = Book.stock
    else:
        sort_column = Book.name
        
    # sorting order 
    if order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # pagination 
    offset = (page - 1) * limit
    
    # final filtering
    books = query.offset(offset).limit(limit).all()
    
    return books

def get_specific_book(bookid : int, db: Session):
    book = db.query(Book).filter(Book.id == bookid).first()
    if not book:
        raise BookNotFound()
    return book

def update_book_by_id_admin(bookid : int,
                      bookobj : BookUpdate,
                      db: Session):
    book = db.query(Book).filter(Book.id==bookid).first()
    
    if not book:
        raise BookNotFound()
    
    updated_data = bookobj.model_dump(exclude_unset=True)
    
    for k,v in updated_data.items():
        setattr(book,k,v)

    db.commit()
    db.refresh(book)
    
    return book

def delete_book_admin(bookid : int,
                db: Session):
    
    book = db.query(Book).filter(Book.id==bookid).first()
    
    if not book:
        raise BookNotFound()
    
    db.delete(book)
    db.commit()
    
    return 
