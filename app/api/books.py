from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate, BookResponse
from app.core.dependencies import require_roles
from app.core.roles import Roles

from app.exceptions.book import BookNotFound, BookOutOfStock

router = APIRouter(prefix="/books", tags=["Books"])

@router.post("/", 
            response_model=BookResponse, 
            status_code=status.HTTP_201_CREATED
            )
def create_book(book: BookCreate, db: Session = Depends(get_db), user= Depends(require_roles(Roles.ADMIN,Roles.LIBRARIAN))):
    db_book_obj = Book(
        name = book.name,
        isbn = book.isbn,
        stock = book.stock
    )
    db.add(db_book_obj)
    db.commit()
    db.refresh(db_book_obj)
    
    return db_book_obj

@router.get("/", response_model=list[BookResponse], 
            status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def get_books(
    request: Request
    ,search: str | None = Query(None, description = "Search a book with book name or ISBN")
    ,in_stock: bool | None = Query(None, description = "Filter books by stock > 0")
    ,sort_by: str = Query("name", description="Sort by name or stock") 
    ,order: str = Query("asc", description="asc or desc")
    ,page: int = Query(1, ge=1)
    ,limit: int = Query(10, ge=1, le=100)
    ,db: Session = Depends(get_db)
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

@router.get("/{book_id}",response_model=BookResponse, 
            status_code = status.HTTP_200_OK)
@limiter.limit("5/minute")
def get_book_by_id(request: Request, bookid : int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == bookid).first()
    if not book:
        raise BookNotFound("Book not Found!")
    return book

@router.put("/{book_id}", 
            response_model=BookUpdate )
def update_book_by_id(bookid : int,
                      bookobj : BookUpdate,
                      db: Session = Depends(get_db),
                      user= Depends(require_roles(Roles.ADMIN,Roles.LIBRARIAN))):
    book = db.query(Book).filter(Book.id==bookid).first()
    
    if not book:
        raise BookNotFound("Book not Found!")
    
    updated_data = bookobj.model_dump(exclude_unset=True)
    
    for k,v in updated_data.items():
        setattr(book,k,v)

    db.commit()
    db.refresh(book)
    
    return book

@router.delete("/{book_id}")
def delete_book(bookid : int,
                db: Session = Depends(get_db),
                user= Depends(require_roles(Roles.ADMIN,Roles.LIBRARIAN))):
    
    book = db.query(Book).filter(Book.id==bookid).first()
    
    if not book:
        raise BookNotFound("Book not Found!")
    
    db.delete(book)
    db.commit()
    
    return {"message": "Book Deleted!"}
