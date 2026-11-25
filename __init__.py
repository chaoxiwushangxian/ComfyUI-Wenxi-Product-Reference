"""ComfyUI entry point for the Wenxi product reference prompt node."""
from .product_reference import product_reference_prompt


class ProductReferencePrompt:
    CATEGORY = "Wenxi"
    FUNCTION = "apply"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    DESCRIPTION = "根据提示词和九个参考图空位标记，补充商品保真描述。"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"forceInput": True}),
                "slots": ("STRING", {"forceInput": True}),
            }
        }

    def apply(self, prompt, slots):
        return (product_reference_prompt(prompt, slots),)


NODE_CLASS_MAPPINGS = {"WenxiProductReferencePrompt": ProductReferencePrompt}
NODE_DISPLAY_NAME_MAPPINGS = {"WenxiProductReferencePrompt": "文系商品参考图"}

