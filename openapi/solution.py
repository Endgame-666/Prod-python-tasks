import uvicorn
from fastapi import FastAPI, Response, Query, Path
from fastapi.responses import JSONResponse
from http import HTTPStatus
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from enum import StrEnum, auto, Enum
import os
import json

from typing import List, Union, Optional
from pydantic import BaseModel, Field


class ValidationError(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str

class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]] = None

class Specie(Enum):
    """
    Вид дерева.
    """
    ALDER = "alder"
    BIRCH = "birch"
    CEDAR = "cedar"
    FIR = "fir"
    MAPLE = "maple"
    OAK = "oak"
    PINE = "pine"
    SPRUCE = "spruce"
    WILLOW = "willow"

class Tree(BaseModel):
    """Сущность дерева."""
    id: int = Field(..., ge=0.0, title="Id")
    specie: List[Specie] = Field(..., examples=["spruce"])
    months: int = Field(..., gt=0, title="Months", examples=[23])
    meters: float = Field(..., gt=0.0, title="Meters", examples=[0.4])
    class Config:
        schema_extra = {
            "allOf": [
                {
                    "$ref": "#/components/schemas/Specie"
                }
            ]
        }



class Product(BaseModel):
    """Сущность товара."""
    tree_id: int = Field(..., ge=0, title="Tree Id")
    price: float = Field(..., ge=0.0, title="Price", examples=[4999])
    description: Optional[str] = Field(
        default=None,
        max_length=255,
        min_length=15,
        examples=["Неприхотливое дерево для Вашего сада."],
        title="Description"
    )


class Version(BaseModel):
    """Версия сервиса."""
    major: int = Field(..., ge=0, title="Major")
    minor: int = Field(0, ge=0, title="Minor")
    patch: int = Field(0, ge=0, title="Patch")

def create_app() -> FastAPI:
    """Фабрика приложения."""
    app = FastAPI()

    # Считаем спецификацию из файла
    openapi_path = os.path.join(os.path.dirname(__file__), "docs", "openapi.json")
    with open(openapi_path, encoding="utf-8") as f:
        openapi_spec = json.load(f)

    def custom_openapi():
        return openapi_spec
    app.openapi = custom_openapi

    return app

def create__app() -> FastAPI:
    """Фабрика приложения."""
    app = FastAPI(
        title="Kesha and co.",
        version="2024.12.6"
    )

    @app.get("/system/healthcheck", tags=["system"], summary="Healtcheck", description="Проверить, что система активна.", response_class=Response, status_code=204)
    async def healthcheck():
        return Response(status_code=204)

    @app.get("/system/version", tags=["system"], summary="Get Version", description="Получить версию системы.", response_model=Version)
    async def get_version():
        return JSONResponse(Response(status_code=200, content=Version(major=0, minor=0, patch=0)))

    @app.put("/warehouse", tags=["warehouse"], summary="Update Tree", description="Обновить информацию о дереве.", response_model=None)
    async def update_tree(tree: Tree):
        return Response(status_code=200, content=None)

    @app.get("/warehouse", tags=["warehouse"], summary="Get Trees", description="Получить деревья со склада.",
             response_model=List[Tree])
    async def get_trees(
            id: Optional[int] = Query(default=None, ge=0),
            specie: Optional[Specie] = Query(default=None),
            min_months: Optional[int] = Query(default=None, gt=0),
            max_months: Optional[int] = Query(default=None, gt=0),
            min_meters: Optional[float] = Query(default=None, gt=0.0),
            max_metres: Optional[float] = Query(default=None, gt=0.0)
    ):
        return [
            Tree(id=1, specie="oak", months=12, meters=2.5),
            Tree(id=2, specie="pine", months=24, meters=3.0)
        ]
    @app.get("/warehouse/{id}", tags=["warehouse"], summary="Get Tree", description="Получить дерево со склада.", response_model=Tree)
    async def get_tree(id: int = Path(..., title="Id", ge=0)):
        return Tree(id=1, specie="oak", months=12, meters=2.5)

    @app.delete("/warehouse/{id}", tags=["warehouse"], summary="Delete Tree", description="Удалить дерево со склада.", response_class=Response, status_code=204)
    async def delete_tree(id: int = Path(..., title="Id", ge=0)):
        return Response(status_code=204)

    @app.put("/products", tags=["products"], summary="Update Product", description="Обновить информацию о продукте.", response_model=None)
    async def update_product(product: Product):
        return Response(status_code=200, content=None)

    @app.get("/products", tags=["products"], summary="Get Products", description="Получить список продуктов.",
             response_model=List[Product])
    async def get_products(
            tree_id: Optional[int] = Query(default=None, ge=0),
            min_price: Optional[float] = Query(default=None, ge=0),
            max_price: Optional[float] = Query(default=None, ge=0),
    ):
        return [
            Product(tree_id=1, price=100.0, description="Example product 1"),
            Product(tree_id=2, price=200.0, description="Example product 2")
        ]
    @app.get("/products/{id}", tags=["products"], summary="Get Product", description="Получить продукт.",
             response_model=Product)
    async def get_product(
            tree_id: int = Query(..., ge=0),
    ):
        return Product(tree_id=1, price=100.0, description="Example product 1")

    @app.delete("/products/{id}", tags=["products"], summary="Delete Product", description="Удалить информацию о продукте.", response_class=Response, status_code=204)
    async def delete_product(tree_id: int = Query(..., ge=0)):
        return Response(status_code=204)

    @app.post(
        "/actualization/price",
        tags=["actualization"],
        summary="Actualize Price",
        description="Актуализировать стоимость товаров.",
        response_class=Response,
        status_code=202,
        responses={
            202: {
                "description": "Successful Response",
                "content": {
                    "application/json": {
                        "schema": {}
                    }
                }
            }
        }
    )
    async def actualize_price(tree_id: Optional[int] = Query(default=int, ge=0)):
        return Response(status_code=202)

    return app


# def test():
#     f1 = open("docs/1.txt")
#     f2 = open("docs/2.txt")
#     for l1, l2 in zip(f1, f2):
#         if l1 == l2:
#             continue
#         else:
#             print(l1, l2)

def main() -> None:
    """Запустить сервер."""
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)

# def root() -> Path:
#     """Получить корень задачи."""
#     return Path(__file__).parent
# def test(root: Path):
#     path = root / "docs" / "openapi.json"
#     with path.open() as file:
#         return json.load(file)


if __name__ == "__main__":
    main()