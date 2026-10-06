"""Generic image file quality inspection, not medical-image interpretation."""
from pathlib import Path
from PIL import Image,ImageStat
SUPPORTED={".png",".jpg",".jpeg",".tif",".tiff"}
ALL_SUPPORTED=SUPPORTED|{".dcm"}
def inspect_image(path):
    f=Path(path)
    if f.suffix.lower()==".dcm":
        try: import pydicom
        except ImportError as exc: raise ValueError("DICOM inspection requires pip install -r requirements-optional.txt") from exc
        pixels=pydicom.dcmread(str(f)).pixel_array
        return {"file_name":f.name,"format":"DICOM","width":int(pixels.shape[-1]),"height":int(pixels.shape[-2]),"channels":1,"mean_intensity":float(pixels.mean()),"std_intensity":float(pixels.std()),"notice":"Pixel QC only; metadata omitted and no diagnosis is performed."}
    if f.suffix.lower() not in SUPPORTED: raise ValueError("Use PNG, JPEG, TIFF, or DICOM (.dcm with optional pydicom)")
    with Image.open(f) as im: im.verify()
    with Image.open(f) as im:
        stat=ImageStat.Stat(im.convert("L"))
        return {"file_name":f.name,"format":im.format,"width":im.width,"height":im.height,"channels":len(im.getbands()),"mean_intensity":round(stat.mean[0],4),"std_intensity":round(stat.stddev[0],4),"notice":"Generic quality statistics only; no tumor classification."}
def inspect_directory(path):
    root=Path(path)
    if not root.is_dir(): raise ValueError(f"Not a directory: {root}")
    return [inspect_image(str(f)) for f in sorted(root.rglob("*")) if f.is_file() and f.suffix.lower() in ALL_SUPPORTED]
