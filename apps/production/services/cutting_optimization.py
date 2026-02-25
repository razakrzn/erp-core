from __future__ import annotations

from pathlib import Path


def _round_dim(value: float) -> float:
    return round(max(float(value), 0.0), 3)


def _extract_parts_from_doc(doc) -> list[dict]:
    from shapely.geometry import Polygon

    parts = []
    msp = doc.modelspace()

    for entity in msp.query("LWPOLYLINE"):
        if not entity.closed:
            continue
        points = [(p[0], p[1]) for p in entity.get_points()]
        if len(points) < 3:
            continue
        polygon = Polygon(points)
        if not polygon.is_valid or polygon.area <= 0:
            continue
        minx, miny, maxx, maxy = polygon.bounds
        width = _round_dim(maxx - minx)
        height = _round_dim(maxy - miny)
        if width > 0 and height > 0:
            parts.append({"width": width, "height": height, "quantity": 1})

    for entity in msp.query("CIRCLE"):
        diameter = _round_dim(entity.dxf.radius * 2)
        if diameter > 0:
            parts.append({"width": diameter, "height": diameter, "quantity": 1})

    for entity in msp.query("SPLINE"):
        try:
            points = list(entity.flattening(0.5))
        except Exception:
            continue
        if len(points) < 2:
            continue
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        width = _round_dim(maxx - minx)
        height = _round_dim(maxy - miny)
        if width > 0 and height > 0:
            parts.append({"width": width, "height": height, "quantity": 1})

    return parts


def _load_doc(file_path: Path):
    import ezdxf

    suffix = file_path.suffix.lower()
    if suffix == ".dxf":
        return ezdxf.readfile(file_path)

    if suffix == ".dwg":
        try:
            from ezdxf.addons import odafc

            return odafc.readfile(file_path)
        except Exception as exc:  # pragma: no cover - depends on ODA converter
            raise ValueError(
                "DWG parsing requires ODA File Converter support in ezdxf. "
                "Install/configure ODA converter or upload DXF."
            ) from exc

    raise ValueError("Unsupported CAD file format. Upload .dxf or .dwg")


def _build_default_sheets() -> list[dict]:
    return [{"name": "Default Sheet", "width": 3000.0, "height": 1500.0, "quantity": 1}]


def run_cutting_optimization(file_path: str, stock_sheets: list[dict] | None = None) -> dict:
    import numpy as np
    from rectpack import newPacker

    path = Path(file_path)
    doc = _load_doc(path)
    parts = _extract_parts_from_doc(doc)

    if not parts:
        return {
            "parts": [],
            "used_bins": [],
            "placements": [],
            "unplaced_parts": [],
            "summary": {
                "total_parts": 0,
                "placed_parts": 0,
                "unplaced_parts": 0,
                "utilization_percent": 0.0,
            },
        }

    normalized_sheets = stock_sheets or _build_default_sheets()

    packer = newPacker(rotation=True)

    expanded_parts = []
    for idx, part in enumerate(parts):
        quantity = int(part.get("quantity", 1) or 1)
        width = _round_dim(part["width"])
        height = _round_dim(part["height"])
        for part_index in range(quantity):
            rid = f"part-{idx + 1}-{part_index + 1}"
            expanded_parts.append({"rid": rid, "width": width, "height": height})
            packer.add_rect(width, height, rid=rid)

    sheet_dimensions = []
    for sheet_idx, sheet in enumerate(normalized_sheets):
        quantity = int(sheet.get("quantity", 1) or 1)
        width = _round_dim(sheet["width"])
        height = _round_dim(sheet["height"])
        for q in range(quantity):
            bin_id = f"sheet-{sheet_idx + 1}-{q + 1}"
            sheet_dimensions.append({"sheet": bin_id, "width": width, "height": height})
            packer.add_bin(width, height, bid=bin_id)

    packer.pack()

    placed = []
    used_bin_ids = set()
    for sheet_index, x, y, width, height, rid in packer.rect_list():
        bin_id = sheet_dimensions[sheet_index]["sheet"]
        used_bin_ids.add(bin_id)
        placed.append(
            {
                "part_id": rid,
                "x": _round_dim(x),
                "y": _round_dim(y),
                "width": _round_dim(width),
                "height": _round_dim(height),
                "sheet": bin_id,
            }
        )

    placed_ids = {item["part_id"] for item in placed}
    unplaced = [item for item in expanded_parts if item["rid"] not in placed_ids]

    used_bins = [item for item in sheet_dimensions if item["sheet"] in used_bin_ids]
    placed_area = float(np.sum([p["width"] * p["height"] for p in placed])) if placed else 0.0
    used_bin_area = float(np.sum([b["width"] * b["height"] for b in used_bins])) if used_bins else 0.0
    utilization = round((placed_area / used_bin_area) * 100, 2) if used_bin_area else 0.0

    return {
        "parts": parts,
        "used_bins": used_bins,
        "placements": placed,
        "unplaced_parts": unplaced,
        "summary": {
            "total_parts": len(expanded_parts),
            "placed_parts": len(placed),
            "unplaced_parts": len(unplaced),
            "utilization_percent": utilization,
        },
    }
