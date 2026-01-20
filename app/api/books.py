from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate, BookResponse

router = APIRouter(prefix="/books", tags=["Books"])

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book_obj = Book(
        name = book.name,
        isbn = book.isbn,
        stock = book.stock
    )
    db.add(db_book_obj)
    db.commit()
    db.refresh(db_book_obj)
    
    return db_book_obj

@router.get("/", response_model=list[BookResponse], status_code=status.HTTP_200_OK)
def get_books(db: Session = Depends(get_db)):
    return db.query(Book).all()

@router.get("/{book_id}",response_model=BookResponse, status_code = status.HTTP_200_OK)
def get_book_by_id(bookid : int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == bookid).first()
    if not book:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail = "Book not Found!")
    return book

@router.put("/{book_id}", response_model=BookUpdate )
def update_book_by_id(bookid : int,
                      bookobj : BookUpdate,
                      db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id==bookid).first()
    
    if not book:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail = "Book not Found!")
    
    updated_data = bookobj.model_dump(exclude_unset=True)
    
    for k,v in updated_data.items():
        setattr(book,k,v)

    db.commit()
    db.refresh(book)
    
    return book

@router.delete("/{book_id}")
def delete_book(bookid : int,
                db: Session = Depends(get_db)):
    
    book = db.query(Book).filter(Book.id==bookid).first()
    
    if not book:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail = "Book not Found!")
    
    db.delete(book)
    db.commit()
    
    return None
