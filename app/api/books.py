from fastapi import APIRouter, Depends, status, Query, Request
from sqlalchemy.orm import Session

from app.schemas.book import BookCreate, BookUpdate, BookResponse

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.response import success_response
from app.core.dependencies import require_roles
from app.core.roles import Roles

from app.controllers.book_controller import(
    create_book_admin,
    search_books,
    get_specific_book,
    update_book_by_id_admin,
    delete_book_admin
)

router = APIRouter(prefix="/books", tags=["Books"])

@router.post("/", 
            response_model=BookResponse, 
            status_code=status.HTTP_201_CREATED
            )
def create_book(book: BookCreate, db: Session = Depends(get_db), user= Depends(require_roles(Roles.ADMIN,Roles.LIBRARIAN))):
    new_book = create_book_admin(book = book, db = db)
    return success_response(
        data = BookResponse.model_validate(new_book).model_dump(mode="json")
    )


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
    books = search_books(db = db, search = search, in_stock = in_stock, sort_by = sort_by, order = order, page = page, limit = limit)
    return success_response(
        data = 
        [ BookResponse.model_validate(i).model_dump(mode="json") for i in books ]
    )

@router.get("/{book_id}",response_model=BookResponse, 
            status_code = status.HTTP_200_OK)
@limiter.limit("5/minute")
def get_book_by_id(request: Request, bookid : int, db: Session = Depends(get_db)):
    book = get_specific_book(bookid = bookid, db = db)
    return success_response(
            data = BookResponse.model_validate(book).model_dump(mode="json")
        )
    
@router.put("/{book_id}", 
            response_model=BookUpdate )
def update_book_by_id(bookid : int,
                      bookobj : BookUpdate,
                      db: Session = Depends(get_db),
                      user= Depends(require_roles(Roles.ADMIN,Roles.LIBRARIAN))):
    book = update_book_by_id_admin(bookid = bookid, bookobj = bookobj, db = db)
    
    return success_response(
            data = BookResponse.model_validate(book).model_dump(mode="json")
        )

@router.delete("/{book_id}")
def delete_book(bookid : int,
                db: Session = Depends(get_db),
                user= Depends(require_roles(Roles.ADMIN,Roles.LIBRARIAN))):
    delete_book_admin(bookid = bookid, db = db)
    return success_response(message="Book Deleted!")
