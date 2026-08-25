import sys

sys.path.insert(0, r"D:\Akshit Personal OS\backend")
sys.path.insert(0, r"D:\Akshit Personal OS\backend\scripts")

from inspect_new_primaries import fetch, parse

CHECKS = {
    "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_computer-vision/ssd.md":
        ["average precision", "map", "non-maximum", "iou"],
    "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_computer-vision/kaggle-cifar10.md":
        ["read_image", "255", "float", "transpose", "permute", "batch"],
    "https://scikit-image.org/docs/stable/user_guide/numpy_images.html":
        ["numpy array", "rows", "columns", "shape", "width", "height", "resolution", "pixel"],
    "https://raw.githubusercontent.com/huggingface/course/main/chapters/en/chapter3/1.mdx":
        ["encoder", "decoder", "seq2seq", "generation", "understanding"],
    "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_recurrent-modern/encoder-decoder.md":
        ["encoder", "decoder", "seq2seq", "generation"],
    "https://www.promptingguide.ai/risks/hallucination":
        ["hallucinat", "fabricat", "fact", "grounding", "cite"],
    "https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview":
        ["schema", "input_schema", "is_error", "tool_result", "parameter", "stop_reason"],
    "https://www.anthropic.com/engineering/building-effective-agents":
        ["stop", "maximum", "iterations", "budget", "terminat", "halt"],
    "https://owasp.org/www-project-top-10-for-large-language-model-applications/":
        ["prompt injection", "llm01", "permission", "scope", "security"],
    "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_computer-vision/resnet.md":
        ["degradation", "residual", "skip", "identity"],
    "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_computer-vision/rcnn.md":
        ["instance", "semantic segmentation", "mask r-cnn", "roialign"],
    "https://raw.githubusercontent.com/d2l-ai/d2l-en/master/chapter_convolutional-modern/resnet.md":
        ["degradation", "residual", "identity"],
}

for url, terms in CHECKS.items():
    cls, code, payload = fetch(url)
    if cls != "OK":
        print(f"{code} FAIL {url[:80]}")
        continue
    _h, v = parse(payload)
    low = v.lower()
    hits = {t: (t.lower() in low) for t in terms}
    print(f"{len(v):>7}c {url.split('/')[-1][:45]:45} {hits}")
