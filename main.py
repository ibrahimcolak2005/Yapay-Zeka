from datetime import date
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import TodoModel

# Tabloları oluştur
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo API", description="Basit bir Görev Yönetim API'si")

# ---------- Pydantic Şemaları ----------

class TodoCreate(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False
    due_date: date | None = None

class TodoResponse(TodoCreate):
    id: int

    model_config = {"from_attributes": True}

# ---------- Uç noktalar (Endpoints) ----------

@app.get("/todos", response_model=list[TodoResponse], summary="Tüm görevleri listele")
def list_todos(db: Session = Depends(get_db)):
    """Kayıtlı tüm görevleri döndürür."""
    return db.query(TodoModel).all()


@app.post("/todos", response_model=TodoResponse, status_code=201, summary="Yeni görev ekle")
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    """Yeni bir görev oluşturur ve döndürür."""
    db_todo = TodoModel(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.delete("/todos/{todo_id}", response_model=TodoResponse, summary="Görev sil")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """Belirtilen id'ye sahip görevi siler ve silinen görevi döndürür."""
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Görev bulunamadı")
    db.delete(db_todo)
    db.commit()
    return db_todo


# ---------- Statik dosyalar & Ana sayfa ----------

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def root():
    return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
