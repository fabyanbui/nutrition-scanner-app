with open("apps/api/src/main.py", "r") as f:
    content = f.read()

content = content.replace("from sse_starlette.sse import EventSourceResponse", "from sse_starlette.sse import EventSourceResponse\nfrom .image_quality import analyze_image_quality")

old_heuristics = """        # Run heuristic quality check before ML graph (Mocking simple heuristics)
        file_size_kb = len(image_bytes) / 1024
        if file_size_kb < 10:
            await emit({"agent": "quality_heuristic", "status": "completed", "warning": "Low resolution image detected."})"""

new_heuristics = """        # Run heuristic quality check before ML graph
        warnings = analyze_image_quality(image_bytes)
        if warnings:
            await emit({"agent": "quality_heuristic", "status": "completed", "warning": " | ".join(warnings)})
        else:
            await emit({"agent": "quality_heuristic", "status": "completed"})"""

content = content.replace(old_heuristics, new_heuristics)

with open("apps/api/src/main.py", "w") as f:
    f.write(content)
