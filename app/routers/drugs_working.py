from fastapi import APIRouter

router = APIRouter()

@router.get("/working/drugs")
def get_working_drugs():
    return [
        {"id": 1, "trade_name": "Abilify 10 mg", "strength": "10mg"},
        {"id": 2, "trade_name": "Abilify 15 mg", "strength": "15mg"}
    ]

@router.get("/drugs")
def get_drugs():
    return [
        {"id": 1, "trade_name": "Abilify 10 mg", "strength": "10mg"},
        {"id": 2, "trade_name": "Abilify 15 mg", "strength": "15mg"}
    ]
