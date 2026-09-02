import vision_agent as va


def test_missing_image_path():
    try:
        va.vision_agent({}, "What is shown?")
    except ValueError as e:
        print("PASS - Missing image path:", e)


def test_invalid_image_path():
    try:
        va.vision_agent(
            {"image_path": "does_not_exist.png"},
            "What is shown?"
        )
    except FileNotFoundError as e:
        print("PASS - Invalid image path:", e)


def test_vlm_failure():
    va.ask_vlm = lambda **kwargs: (_ for _ in ()).throw(
        RuntimeError("Simulated VLM failure")
    )

    result = va.vision_agent(
        {
            "image_path": "test_chart_crop.png",
            "document": "sample.pdf",
            "page": 1,
            "image_id": 1,
            "score": 0.9
        },
        "What is shown?"
    )

    assert "Vision model error" in result["answer"]

    print("PASS - VLM failure handling:", result["answer"])


if __name__ == "__main__":
    test_missing_image_path()
    test_invalid_image_path()
    test_vlm_failure()

    print("\nAll Vision Agent validation tests passed!")
    