from fastapi import APIRouter

router = APIRouter()

@router.get("/drugs")
def get_all_drugs():
    # Return sample data for now
    return [
        {
            "id": 1,
            "trade_name": "Abilify 10 mg 10",
            "price": None,
            "strength": "10 mg",
            "dosage_form": "Tablets",
            "manufacturer": "Otsuka Pharmaceuti",
            "pack_size": "10 Tablets",
            "composition": "Aripiprazole"
        },
        {
            "id": 2,
            "trade_name": "Abilify 15 mg 10",
            "price": None,
            "strength": "15 mg",
            "dosage_form": "Tablets",
            "manufacturer": "Otsuka Pharmaceuti",
            "pack_size": "10 Tablets",
            "composition": "Aripiprazole"
        }
    ]

@router.get("/drugs/search")
def search_drugs(query: str):
    # Simple search in the sample data
    sample_drugs = [
        {
            "id": 1,
            "trade_name": "Abilify 10 mg 10",
            "price": None,
            "strength": "10 mg",
            "dosage_form": "Tablets",
            "manufacturer": "Otsuka Pharmaceuti",
            "pack_size": "10 Tablets",
            "composition": "Aripiprazole"
        },
        {
            "id": 2,
            "trade_name": "Abilify 15 mg 10",
            "price": None,
            "strength": "15 mg",
            "dosage_form": "Tablets",
            "manufacturer": "Otsuka Pharmaceuti",
            "pack_size": "10 Tablets",
            "composition": "Aripiprazole"
        }
    ]
    
    filtered_drugs = [drug for drug in sample_drugs if query.lower() in drug["trade_name"].lower()]
    return filtered_drugs
