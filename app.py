# Simple fastapi server
from fastapi import FastAPI, UploadFile, HTTPException
from config import init_database
from typing import Union, List
from PIL import Image
from Preprocessing import convert_to_image_tensor, invert_image
from models.db import SignatureInDB
from Model import SiameseConvNet, distance_metric, load_model
app = FastAPI()
import math, io, os

@app.on_event("startup")
async def startup():
    await init_database()


@app.get("/")
async def welcome():
    return {"message": "Welcome to my API"}


# Lets create a route for upload signature image. This will be used to upload one image. We will call it from frontend multiple times to upload multiple images.

@app.post("/upload/{customer_id}")
async def upload_signatures(customer_id: str, files: List[UploadFile]):
    signs_path =  []
    try:
        for file in files:
            # save all files in a folder named "signatures"
            file_path = os.path.join(os.getcwd(), "signatures", file.filename)
            with open(file_path, "wb") as f:
                f.write(file.file.read())
            # store the file name in the database
            signs_path.append(file_path)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Something went wrong")

    db_entry = SignatureInDB(name=customer_id, signatures=signs_path)
    await db_entry.create()

    return {"message": "Uploaded"}


@app.post("/verify/{customer_id}")
async def verify_signature(customer_id: str, file: Union[UploadFile,None]):
    if file is None:
        return {"message": "No file uploaded"}
    # check the recieved file with the other files from db.
    input_image = await Image.open(io.BytesIO(await file.read()))
    input_image_tensor = convert_to_image_tensor(
        invert_image(input_image)).view(1, 1, 220, 155)
    data_from_db = await SignatureInDB.find_one(SignatureInDB.name == customer_id)
    if data_from_db is None:
        return {"message": "No signature found"}

    anchor_images = [Image.open(sig) for sig in data_from_db.signatures]  # Here sig will be the path of the image, which we have saved in db.
    anchor_image_tensors = [convert_to_image_tensor(invert_image(x)).view(-1, 1, 220, 155) 
                        for x in anchor_images]
    model = load_model()
    mindist = math.inf
    for anci in anchor_image_tensors:
        f_A, f_X = model.forward(anci, input_image_tensor)
        dist = float(distance_metric(f_A, f_X).detach().numpy())
        mindist = min(mindist, dist)

        if dist <= 0.145139:  # Threshold obtained using Test.py
            return {"match": True, "error": False, "threshold":"%.6f" % (0.145139), "distance":"%.6f"%(mindist)}
    return {"match": False, "error": False, "threshold":0.145139, "distance":round(mindist, 6)}