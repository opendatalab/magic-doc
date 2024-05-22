from flask import Flask, Response, request
import requests

app = Flask(__name__)


@app.route("/path/<path:subpath>")
def handle_path(subpath):
    include_content_type = request.args.get("ct", "false").lower() == "true"
    include_content_disposition = request.args.get("cd", "false").lower() == "true"

    if subpath.endswith(".html"):
        content_type, disposition = "text/html", "inline"
    elif subpath.endswith(".pdf"):
        content_type, disposition = (
            "application/pdf",
            'attachment; filename="document.pdf"',
        )
    elif subpath.endswith(".doc"):
        content_type, disposition = (
            "application/msword",
            'attachment; filename="document.doc"',
        )
    elif subpath.endswith(".docx"):
        content_type, disposition = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            'attachment; filename="document.docx"',
        )
    elif subpath.endswith(".ppt"):
        content_type, disposition = (
            "application/vnd.ms-powerpoint",
            'attachment; filename="presentation.ppt"',
        )
    elif subpath.endswith(".pptx"):
        content_type, disposition = (
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            'attachment; filename="presentation.pptx"',
        )
    elif subpath.endswith(".jpg") or subpath.endswith(".jpeg"):
        content_type, disposition = "image/jpeg", "inline"
    elif subpath.endswith(".png"):
        content_type, disposition = "image/png", "inline"
    else:
        content_type = "text/plain"
        disposition = 'attachment; filename="default.txt"'

    response = Response(f"Requested {subpath}")
    if include_content_type:
        response.headers["Content-Type"] = content_type
    if include_content_disposition:
        response.headers["Content-Disposition"] = disposition

    return response


if __name__ == "__main__":
    # app.run(debug=True, port=6500)
    res = requests.get(
        "https://filesamples.com/samples/document/doc/sample2.doc",
        timeout=10,
        stream=True,
    )
    if res.status_code not in [200]:
        res.raise_for_status()
    print(res.headers.get("Content-Type"))
